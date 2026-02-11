import adapterAuto from '@sveltejs/adapter-auto';

const isGithubPages = process.env.GITHUB_PAGES === 'true';
const repositoryName = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? '';
const basePath = isGithubPages && repositoryName ? `/${repositoryName}` : '';

let adapter = adapterAuto();
if (isGithubPages) {
	try {
		const { default: adapterStatic } = await import('@sveltejs/adapter-static');
		adapter = adapterStatic({
			pages: 'build',
			assets: 'build',
			fallback: '404.html',
			precompress: false,
			strict: false
		});
	} catch (error) {
		console.warn('[svelte-config] adapter-static missing; fallback to adapter-auto.', error);
	}
}

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter,
		paths: {
			base: basePath
		},
		prerender: {
			entries: ['*']
		}
	}
};

export default config;
