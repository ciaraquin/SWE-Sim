<script lang="ts">
	import { onMount } from 'svelte';

	type Simulation = {
		simulation_id: string;
		title: string;
		status: string;
		created_at: string;
	};

	const backendUrl = 'http://localhost:8000';
	let simulations = $state<Simulation[]>([]);
	let title = $state('');
	let loading = $state(true);
	let saving = $state(false);
	let message = $state('');
	let authenticated = $state(true);
	let user = $state<{ login: string; name: string | null } | null>(null);
	let modalOpen = $state(false);
	let description = $state('');
	let teamSize = $state(3);
	let difficulty = $state('Intermediate');

	const examples = [
		{
			title: 'Campus events platform',
			description: 'Build a platform where students can discover, create, and RSVP to campus events.',
			teamSize: 4,
			difficulty: 'Beginner'
		},
		{
			title: 'Team task tracker',
			description: 'Create a collaborative issue tracker with assignments, priorities, and progress updates.',
			teamSize: 3,
			difficulty: 'Intermediate'
		},
		{
			title: 'Production analytics dashboard',
			description: 'Design a dashboard that helps an engineering team investigate reliability and performance trends.',
			teamSize: 5,
			difficulty: 'Advanced'
		}
	];

	onMount(loadPage);

	async function loadPage() {
		const userResponse = await fetch(`${backendUrl}/auth/me`, { credentials: 'include' });
		if (!userResponse.ok) {
			authenticated = false;
			loading = false;
			return;
		}
		user = (await userResponse.json()).user;
		await loadSimulations();
	}

	async function loadSimulations() {
		loading = true;
		const response = await fetch(`${backendUrl}/simulations`, { credentials: 'include' });
		if (response.status === 401) {
			authenticated = false;
			loading = false;
			return;
		}
		if (response.ok) simulations = (await response.json()).simulations;
		loading = false;
	}

	function chooseExample(example: (typeof examples)[number]) {
		title = example.title;
		description = example.description;
		teamSize = example.teamSize;
		difficulty = example.difficulty;
	}

	async function createSimulation() {
		if (!title.trim() || !description.trim()) {
			message = 'Give your simulation a title first.';
			return;
		}

		saving = true;
		message = '';
		const response = await fetch(`${backendUrl}/simulations`, {
			method: 'POST',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ title: title.trim(), description: description.trim(), team_size: teamSize, difficulty })
		});

		if (response.ok) {
			title = '';
			description = '';
			teamSize = 3;
			difficulty = 'Intermediate';
			modalOpen = false;
			await loadSimulations();
		} else {
			message = 'The simulation could not be created.';
		}
		saving = false;
	}

	async function logout() {
		await fetch(`${backendUrl}/auth/logout`, { method: 'POST', credentials: 'include' });
		user = null;
		authenticated = false;
	}
</script>

<svelte:head>
	<title>Simulations | SWE Sim</title>
	<meta name="description" content="Start and review your SWE Sim practice projects." />
</svelte:head>

<section class="simulations-page">
	<p class="eyebrow">Practice workspace</p>
	<h1>Your simulations</h1>
	<p class="intro">Start a project and work through the decisions real engineering teams make every day.</p>

	{#if !authenticated}
		<div class="empty-state">
			<h2>Sign in to begin</h2>
			<p>Your simulations are saved to your GitHub account.</p>
			<a href="http://localhost:8000/auth/github">Sign in with GitHub <span aria-hidden="true">&#8594;</span></a>
		</div>
	{:else}
		<div class="account-bar">
			<span>Signed in as <strong>{user?.name || user?.login}</strong></span>
			<button type="button" class="sign-out" onclick={logout}>Sign out</button>
		</div>
		<button class="new-simulation" type="button" onclick={() => { modalOpen = true; message = ''; }}>New simulation <span aria-hidden="true">+</span></button>
		{#if modalOpen}
			<div class="modal-backdrop" role="presentation" onclick={(event) => { if (event.target === event.currentTarget) modalOpen = false; }}>
				<dialog open class="modal" aria-labelledby="modal-title">
					<div class="modal-header">
						<div><p class="eyebrow">Project setup</p><h2 id="modal-title">Start a simulation</h2></div>
						<button class="close" type="button" aria-label="Close" onclick={() => modalOpen = false}>×</button>
					</div>
					<p class="modal-copy">Choose an example to get moving, or shape a project of your own.</p>
					<div class="examples">
						{#each examples as example}
							<button class="example" type="button" onclick={() => chooseExample(example)}>
								<strong>{example.title}</strong><span>{example.difficulty} · {example.teamSize} teammates</span>
							</button>
						{/each}
					</div>
					<form class="create-form" onsubmit={(event) => { event.preventDefault(); createSimulation(); }}>
						<label for="simulation-title">Project title</label>
						<input id="simulation-title" bind:value={title} maxlength="120" placeholder="e.g. Release a new feature" />
						<label for="simulation-description">Description</label>
						<textarea id="simulation-description" bind:value={description} maxlength="1000" rows="3" placeholder="What is the team building?"></textarea>
						<div class="field-grid">
							<div><label for="team-size">Team size</label><input id="team-size" type="number" min="1" max="10" bind:value={teamSize} /></div>
							<div><label for="difficulty">Difficulty</label><select id="difficulty" bind:value={difficulty}><option>Beginner</option><option>Intermediate</option><option>Advanced</option></select></div>
						</div>
						{#if message}<p class="message">{message}</p>{/if}
						<button class="submit" type="submit" disabled={saving}>{saving ? 'Creating...' : 'Create simulation'}</button>
					</form>
				</dialog>
			</div>
		{/if}

		{#if loading}
			<p class="muted">Loading simulations...</p>
		{:else if simulations.length === 0}
			<div class="empty-state">
				<h2>No simulations yet</h2>
				<p>Your first project starts with a title above.</p>
			</div>
		{:else}
			<div class="simulation-list">
				{#each simulations as simulation}
					<article class="simulation-row">
						<div>
							<h2>{simulation.title}</h2>
							<p>{new Date(simulation.created_at).toLocaleDateString()}</p>
						</div>
						<span class="status">{simulation.status}</span>
					</article>
				{/each}
			</div>
		{/if}
	{/if}
</section>

<style>
	.simulations-page { width: min(900px, calc(100% - 3rem)); margin: 0 auto; padding: clamp(5rem, 12vw, 9rem) 0; }
	.eyebrow { margin: 0 0 1.5rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; }
	h1 { margin: 0; font-size: clamp(3rem, 7vw, 6rem); font-weight: 400; letter-spacing: -0.04em; line-height: 0.95; }
	.intro { max-width: 34rem; margin: 1.5rem 0 3rem; color: #526057; font-size: 1.1rem; line-height: 1.6; }
	.create-form { padding: 1.25rem 0 2rem; border-bottom: 1px solid rgba(32, 42, 37, 0.2); }
	.create-form label { display: block; margin-bottom: 0.6rem; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; }
	input, button { border: 1px solid rgba(32, 42, 37, 0.25); padding: 0.85rem 1rem; font: inherit; }
	input { min-width: 0; flex: 1; background: #fff9ed; }
	button { background: #202a25; color: #f5f1e8; cursor: pointer; }
	button:disabled { cursor: wait; opacity: 0.65; }
	.account-bar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.75rem; }
	.sign-out { padding: 0.55rem 0.75rem; background: transparent; color: #202a25; }
	.simulation-list { border-bottom: 1px solid rgba(32, 42, 37, 0.2); }
	.simulation-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.25rem 0; border-bottom: 1px solid rgba(32, 42, 37, 0.16); }
	.simulation-row:last-child { border-bottom: 0; }
	.new-simulation { margin-bottom: 2rem; padding: 0.9rem 1.1rem; }
	.simulation-row h2 { margin: 0; font-size: 1.3rem; font-weight: 400; }
	.simulation-row p, .muted, .message, .empty-state p { margin: 0.35rem 0 0; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.75rem; }
	.status { color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
	.empty-state { margin-top: 2rem; padding: 2rem 0; border-top: 1px solid rgba(32, 42, 37, 0.16); }
	.empty-state h2 { margin: 0; font-size: 1.5rem; font-weight: 400; }
	.empty-state a { display: inline-block; margin-top: 1.5rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; font-weight: 700; text-decoration: none; }
	.back-link { display: inline-block; margin-top: 3rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; font-weight: 700; text-decoration: none; }
	.back-link:hover, .back-link:focus-visible { text-decoration: underline; }
	.message { color: #a33f48; }
	.modal-backdrop { position: fixed; z-index: 10; inset: 0; display: grid; place-items: center; padding: 1rem; background: rgba(32, 42, 37, 0.45); }
	.modal { width: min(620px, 100%); max-height: 90vh; margin: 0; overflow-y: auto; padding: 2rem; border: 0; background: #f5f1e8; box-shadow: 0 1rem 3rem rgba(32, 42, 37, 0.2); }
	.modal-header { display: flex; justify-content: space-between; gap: 1rem; }
	.modal-header .eyebrow { margin-bottom: 0.75rem; }
	.modal h2 { margin: 0; font-size: 2rem; font-weight: 400; }
	.close { padding: 0.2rem 0.6rem; background: transparent; color: #202a25; font-size: 1.5rem; line-height: 1; }
	.modal-copy { color: #526057; line-height: 1.5; }
	.examples { display: grid; gap: 0.5rem; margin: 1.25rem 0 1.5rem; }
	.example { display: flex; flex-direction: column; align-items: flex-start; gap: 0.25rem; padding: 0.85rem; background: #fff9ed; color: #202a25; text-align: left; }
	.example span { color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.7rem; }
	.create-form { display: grid; gap: 0.55rem; padding: 1.25rem 0 0; border-top: 1px solid rgba(32, 42, 37, 0.2); }
	textarea, select { width: 100%; border: 1px solid rgba(32, 42, 37, 0.25); padding: 0.85rem 1rem; background: #fff9ed; font: inherit; }
	.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.5rem; }
	.field-grid input { width: 100%; }
	.submit { margin-top: 0.75rem; }
	@media (max-width: 600px) { .simulations-page { width: min(100% - 2rem, 900px); } .simulation-row { align-items: flex-start; flex-direction: column; } }
</style>