<script lang="ts">
	import { onMount } from 'svelte';
	import githubLogo from '$lib/assets/github.png';
    import favicon from '$lib/assets/favicon.png';

	const backendUrl = 'http://localhost:8000';
	let user = $state<{ login: string; name: string | null } | null>(null);
	let simulations = $state<{ simulation_id: string; title: string; status: string }[]>([]);
	let newTitle = $state('');
	let simulationError = $state('');

	onMount(async () => {
		const response = await fetch(`${backendUrl}/auth/me`, { credentials: 'include' });
		if (response.ok) {
			user = (await response.json()).user;
			await loadSimulations();
		}
	});

	async function loadSimulations() {
		const response = await fetch(`${backendUrl}/simulations`, { credentials: 'include' });
		if (response.ok) simulations = (await response.json()).simulations;
	}

	async function startSimulation() {
		simulationError = '';
		const response = await fetch(`${backendUrl}/simulations`, {
			method: 'POST',
			credentials: 'include',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ title: newTitle || 'Untitled simulation' })
		});
		if (!response.ok) {
			simulationError = 'Unable to create simulation.';
			return;
		}
		newTitle = '';
		await loadSimulations();
	}

	async function logout() {
		await fetch(`${backendUrl}/auth/logout`, {
			method: 'POST',
			credentials: 'include'
		});
		user = null;
	}
</script>

<svelte:head>
	<title>SWE Sim | Practice software engineering</title>
	<meta name="description" content="A simulation space for practicing software engineering decisions." />
	<link rel="icon" type="image/x-icon" href={favicon} />
</svelte:head>

<section class="hero">
	<div class="hero-copy">
		<p class="eyebrow">A rehearsal space for real engineering work</p>
		<h1>Build better instincts<br /><em>before</em> production.</h1>
		<p class="intro">SWE Sim allows you to practice the skills you'll use in real-world software engineering scenarios.</p>
		{#if user}
			<div class="signed-in">
				<p>Signed in as <strong>{user.name || user.login}</strong></p>
				<button type="button" onclick={logout}>Sign out</button>
			</div>
			<div class="simulations">
				<!-- <div class="simulation-heading">
					<p class="eyebrow">Your simulations</p>
					<form onsubmit={(event) => { event.preventDefault(); startSimulation(); }}>
						<input bind:value={newTitle} aria-label="Simulation title" placeholder="Simulation title" />
						<button type="submit">Start simulation</button>
					</form>
				</div> -->
				{#if simulationError}<p class="error">{simulationError}</p>{/if}
				{#if simulations.length}
					<ul>
						{#each simulations as simulation}
							<li><strong>{simulation.title}</strong><span>{simulation.status}</span></li>
						{/each}
					</ul>
				{:else}
					<p class="empty">No simulations yet.</p>

				{/if}
				<a class="simulations-link" href="/simulations">Explore simulations <span aria-hidden="true">&#8594;</span></a>
			</div>
		{:else}
		<a class="github-button" href="http://localhost:8000/auth/github">
			<span class="github-mark" aria-hidden="true"><img src={githubLogo} alt="" /></span>
			<span>Sign in with GitHub</span>
			<span class="arrow" aria-hidden="true">&#8594;</span>
		</a>
		<p class="note">Your GitHub account will be used to save your progress.</p>
		{/if}
		
	</div>

</section>

<style>
	.hero {
		width: min(1120px, calc(100% - 3rem));
		margin: 0 auto;
		display: grid;
		align-items: center;
		padding: clamp(5rem, 12vw, 9rem) 0 clamp(5rem, 10vw, 8rem);
	}
	.eyebrow {
		margin: 0 0 1.5rem;
		color: #c336a5e2;
		font-family: 'Trebuchet MS', sans-serif;
		font-size: 0.72rem;
		font-weight: 700;
		letter-spacing: 0.14em;
		text-transform: uppercase;
	}
	h1 {
		max-width: 720px;
		margin: 0;
		font-size: clamp(3.4rem, 7vw, 6.7rem);
		font-weight: 400;
		letter-spacing: -0.04em;
		line-height: 0.95;
	}
	h1 em { color: #c336a5e2; font-style: italic; }
	.intro {
		max-width: 31rem;
		margin: 2rem 0 2.25rem;
		color: #526057;
		font-size: 1.15rem;
		line-height: 1.65;
	}
	.github-button {
		display: inline-flex;
		align-items: center;
		gap: 0.85rem;
		padding: 1rem 1.2rem;
		background: #fff9ed;
		color: #202a25;
		font-family: 'Trebuchet MS', sans-serif;
		font-size: 0.85rem;
		font-weight: 700;
		text-decoration: none;
		transition: background 160ms ease, transform 160ms ease;
	}
	.github-button:hover, .github-button:focus-visible { background: #c336a5e2; transform: translateY(-2px); }
	.github-mark { display: inline-flex; width: 1.25rem; height: 1.25rem; }
	.github-mark img { width: 100%; height: 100%; object-fit: contain; }
	.arrow { font-size: 1.2rem; line-height: 0; }
	.note { margin: 0.85rem 0 0; color: #7b857d; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; }
	.simulations-link { display: inline-block; margin-top: 2rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; font-weight: 700; text-decoration: none; }
	.simulations-link:hover, .simulations-link:focus-visible { text-decoration: underline; }
	.signed-in { display: flex; align-items: center; gap: 1rem; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; }
	.signed-in p { margin: 0; }
	button, input { border: 1px solid rgba(32, 42, 37, 0.24); padding: 0.75rem 0.9rem; font: inherit; }
	button { background: #202a25; color: #f5f1e8; cursor: pointer; }
	.simulations { max-width: 42rem; margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid rgba(32, 42, 37, 0.2); }
	.simulation-heading { display: flex; align-items: end; justify-content: space-between; gap: 1rem; }
	.simulation-heading .eyebrow { margin: 0; }
	.simulation-heading form { display: flex; gap: 0.5rem; }
	.simulations ul { margin: 1.5rem 0 0; padding: 0; list-style: none; border-top: 1px solid rgba(32, 42, 37, 0.16); }
	.simulations li { display: flex; justify-content: space-between; padding: 1rem 0; border-bottom: 1px solid rgba(32, 42, 37, 0.16); }
	.simulations li span, .empty, .error { color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.75rem; }
	.error { color: #a33f48; }
	@media (max-width: 700px) { .simulation-heading, .simulation-heading form { align-items: stretch; flex-direction: column; } }
	@media (max-width: 700px) {
		.hero { width: min(100% - 2rem, 1120px); padding-top: 4rem; }
		h1 { font-size: clamp(3.2rem, 16vw, 5rem); }
	}
</style>
