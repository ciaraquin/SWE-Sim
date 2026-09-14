<script lang="ts">
	import githubLogo from '$lib/assets/github.png';
    import favicon from '$lib/assets/favicon.png';
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
		<a class="github-button" href="/auth/github">
			<span class="github-mark" aria-hidden="true"><img src={githubLogo} alt="" /></span>
			<span>Sign in with GitHub</span>
			<span class="arrow" aria-hidden="true">&#8594;</span>
		</a>
		<p class="note">Your GitHub account will be used to save your progress.</p>
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
	@media (max-width: 700px) {
		.hero { width: min(100% - 2rem, 1120px); padding-top: 4rem; }
		h1 { font-size: clamp(3.2rem, 16vw, 5rem); }
	}
</style>
