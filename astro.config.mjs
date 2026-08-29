import react from '@astrojs/react';
import { defineConfig } from 'astro/config';

const useCustomDomain = process.env.CUSTOM_DOMAIN === 'true';

export default defineConfig({
  site: useCustomDomain
    ? 'https://elektro-hubmann.at'
    : 'https://leonhueber.github.io',
  base: useCustomDomain ? undefined : '/elektro-hubmann',
  output: 'static',
  trailingSlash: 'always',
  integrations: [react()],
});
