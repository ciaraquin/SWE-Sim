<script lang="ts">
	import { onMount } from 'svelte';

	type Simulation = {
		simulation_id: string;
		title: string;
		status: string;
		created_at: string;
	};

	const backendUrl = 'http://127.0.0.1:8000';
	let simulations = $state<Simulation[]>([]);
	let title = $state('');
	let loading = $state(true);
	let saving = $state(false);
	let message = $state('');
	let authenticated = $state(true);

	onMount(loadSimulations);

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

	async function createSimulation() {
		if (!title.trim()) {
			message = 'Give your simulation a title first.';
			return;
		}

		saving = true;
		message = '';
		const response = await fetch(`${backendUrl}/simulations`, {
			method: 'POST',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ title: title.trim() })
		});

		if (response.ok) {
			title = '';
			await loadSimulations();
		} else {
			message = 'The simulation could not be created.';
		}
		saving = false;
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
			<a href="http://127.0.0.1:8000/auth/github">Sign in with GitHub <span aria-hidden="true">&#8594;</span></a>
		</div>
	{:else}
		<form class="create-form" onsubmit={(event) => { event.preventDefault(); createSimulation(); }}>
			<label for="simulation-title">New simulation</label>
			<div class="form-row">
				<input id="simulation-title" bind:value={title} maxlength="120" placeholder="e.g. Release a new feature" />
				<button type="submit" disabled={saving}>{saving ? 'Creating...' : 'Start simulation'}</button>
			</div>
			{#if message}<p class="message">{message}</p>{/if}
		</form>

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
	.form-row { display: flex; gap: 0.6rem; }
	input, button { border: 1px solid rgba(32, 42, 37, 0.25); padding: 0.85rem 1rem; font: inherit; }
	input { min-width: 0; flex: 1; background: #fff9ed; }
	button { background: #202a25; color: #f5f1e8; cursor: pointer; }
	button:disabled { cursor: wait; opacity: 0.65; }
	.simulation-list { border-bottom: 1px solid rgba(32, 42, 37, 0.2); }
	.simulation-row { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.25rem 0; border-bottom: 1px solid rgba(32, 42, 37, 0.16); }
	.simulation-row:last-child { border-bottom: 0; }
	.simulation-row h2 { margin: 0; font-size: 1.3rem; font-weight: 400; }
	.simulation-row p, .muted, .message, .empty-state p { margin: 0.35rem 0 0; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.75rem; }
	.status { color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; }
	.empty-state { margin-top: 2rem; padding: 2rem 0; border-top: 1px solid rgba(32, 42, 37, 0.16); }
	.empty-state h2 { margin: 0; font-size: 1.5rem; font-weight: 400; }
	.empty-state a { display: inline-block; margin-top: 1.5rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; font-weight: 700; text-decoration: none; }
	.message { color: #a33f48; }
	@media (max-width: 600px) { .simulations-page { width: min(100% - 2rem, 900px); } .form-row { flex-direction: column; } .simulation-row { align-items: flex-start; flex-direction: column; } }
</style>