<svelte:head>
	<title>About SWE Sim</title>
	<meta name="description" content="Learn about SWE Sim, a simulation for practicing software engineering work." />
</svelte:head>

<section class="about-page">
	<p class="eyebrow">Why SWE Sim exists</p>
		<p class="lead">SWE Sim was created as a capstone project to provide a realistic simulation for practicing software engineering skills.</p>
		<br>
        <div class="details">
        <br>
			<p>In college, students often learn the theory but not the practice of software engineering. SWE Sim was created to allow students to practice skills that software engineers use on a daily basis, without the need of a large-scale project.</p>
			<p>SWE Sim uses LLMs to simulate your teammates, allowing you to practice communication and collaboration skills in a realistic environment.</p>
		</div>
        <br><hr><br>
	<p class="eyebrow">How SWE Sim works</p>
	<div class="workbench" aria-label="SWE Sim practice areas">
		<div class="workbench-label">The Process</div>
		<div class="practice-item"><span>01</span><strong>Sign in with GitHub</strong><small>Allow SWE Sim to create a repository and save your progress.</small></div>
		<div class="practice-item"><span>02</span><strong>Code Generation</strong><small>LLMs will simulate other developers, committing code.</small></div>
		<div class="practice-item"><span>03</span><strong>Your Turn</strong><small>You get to practice your skills in a realistic environment. Practice assigning tasks, reviewing code, and collaborating with your simulated team.</small></div>
	</div><hr><br>
	<a class="back-link" href="/">&#8592; Back to home</a>
</section>

<style>
	.about-page { width: min(900px, calc(100% - 3rem)); margin: 0 auto; padding: clamp(5rem, 12vw, 9rem) 0; }
	.eyebrow { margin: 0 0 1.5rem; color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; }
	.lead, .details p { margin: 0; line-height: 1.65; }
	.lead { font-size: 1.35rem; }
	.details { color: #526057; }
	.details p + p { margin-top: 1.25rem; }
	.workbench { margin: 2.5rem 0; padding-left: 2rem; border-left: 1px solid rgba(32, 42, 37, 0.2); }
	.workbench-label { margin-bottom: 1.5rem; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; }
	.practice-item { display: grid; grid-template-columns: 2.2rem 1fr; padding: 1.25rem 0; border-top: 1px solid rgba(32, 42, 37, 0.16); }
	.practice-item span { color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.7rem; font-weight: 700; }
	.practice-item strong, .practice-item small { grid-column: 2; }
	.practice-item strong { font-size: 1.2rem; font-weight: 400; }
	.practice-item small { margin-top: 0.3rem; color: #647067; font-family: 'Trebuchet MS', sans-serif; font-size: 0.75rem; }
	.back-link { color: #c336a5e2; font-family: 'Trebuchet MS', sans-serif; font-size: 0.8rem; font-weight: 700; text-decoration: none; }
	.back-link:hover, .back-link:focus-visible { text-decoration: underline; }
	@media (max-width: 650px) {
		.about-page { width: min(100% - 2rem, 900px); }
		.workbench { padding-left: 1rem; }
	}
</style>