import type { VariantId } from '../config/site';
import { variants } from '../config/site';

interface Props {
  active?: VariantId;
  baseUrl: string;
}

export default function VersionSwitcher({ active, baseUrl }: Props) {
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`;

  return (
    <nav className="version-switcher" aria-label="Designversion auswählen">
      <span className="version-switcher__label">Designvorschau</span>
      <div className="version-switcher__links">
        {variants.map((variant) => (
          <a
            key={variant.id}
            href={`${normalizedBase}varianten/${variant.id}/`}
            className={active === variant.id ? 'is-active' : undefined}
            aria-current={active === variant.id ? 'page' : undefined}
          >
            {variant.name}
          </a>
        ))}
      </div>
    </nav>
  );
}
