<script lang="ts">
	import favicon from '$lib/assets/favicon.png';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="theme-color" content="#f5f1e8" />
</svelte:head>

<div class="site-shell">
	<header class="site-header">
		<a class="wordmark" href="/" aria-label="SWE Sim home">
			<span><img src={favicon} width="20" height="20" alt="SWE Sim favicon" /></span>
			<span>SWE Sim</span>
		</a>
		<nav aria-label="Main navigation">
			<a href="/">Home</a>
			<a href="/about">About</a>
		</nav>
	</header>

	<main>{@render children()}</main>

	<footer class="site-footer">
		<span>SWE Sim</span>
		<span>Practice the work. Learn the craft.</span>
	</footer>
</div>

<style>
	:global(*) { box-sizing: border-box; }
	:global(body) {
		margin: 0;
		background: #f5f1e8;
		color: #202a25;
		font-family: Georgia, 'Times New Roman', serif;
	}
	:global(a) { color: inherit; }
	.site-shell {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: radial-gradient(circle at 85% 12%, rgba(218, 70, 206, 0.14), transparent 26rem), #f5f1e8;
	}
	.site-header, .site-footer { width: min(1120px, calc(100% - 3rem)); margin: 0 auto; }
	.site-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1.5rem 0;
		border-bottom: 1px solid rgba(32, 42, 37, 0.16);
	}
	.wordmark {
		display: inline-flex;
		align-items: center;
		gap: 0.65rem;
		font-size: 1.2rem;
		font-weight: 700;
		letter-spacing: 0.02em;
		text-decoration: none;
	}
	nav {
		display: flex;
		gap: 1.5rem;
		font-family: 'Trebuchet MS', sans-serif;
		font-size: 0.8rem;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}
	nav a { text-decoration: none; }
	nav a:hover, nav a:focus-visible { color: #c336a5a3; }
	main { flex: 1; }
	.site-footer {
		display: flex;
		justify-content: space-between;
		padding: 1.25rem 0;
		border-top: 1px solid rgba(32, 42, 37, 0.16);
		color: #647067;
		font-family: 'Trebuchet MS', sans-serif;
		font-size: 0.75rem;
		letter-spacing: 0.04em;
	}
	@media (max-width: 600px) {
		.site-header, .site-footer { width: min(100% - 2rem, 1120px); }
		.site-footer { gap: 1rem; flex-direction: column; }
	}
</style>
