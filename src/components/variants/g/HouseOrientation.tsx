import {
  HOUSE_ORIENTATION,
  CONTINUOUS_HOUSE_REVISION,
} from '../../../config/house-orientation';
import type { VersionGStoryState } from '../../../config/version-g-story-assets';
import { houseManifest, posterUrl } from '../../../lib/house-story';

export default function HouseOrientation({
  baseUrl,
  chapter,
}: {
  baseUrl: string;
  chapter: VersionGStoryState;
}) {
  if (houseManifest.revision !== CONTINUOUS_HOUSE_REVISION) return null;
  const { location, subject, regions } = HOUSE_ORIENTATION[chapter];
  return (
    <aside
      className="g-house-orientation"
      data-location={chapter}
      aria-label="Aktueller Blick ins Haus"
      aria-hidden={chapter === 'planning'}
    >
      <div className="g-house-orientation-copy">
        <p>{location}</p>
        <strong>{subject}</strong>
      </div>
      <div className="g-house-overview" aria-hidden="true">
        <img
          src={posterUrl(baseUrl, 'mobile', 0)}
          width={houseManifest.profiles.mobile.width}
          height={houseManifest.profiles.mobile.height}
          alt=""
          decoding="async"
        />
        {regions.map(({ x, y, width, height }, index) => (
          <span
            key={`${chapter}-${index}`}
            className="g-house-region"
            data-focus={Math.max(width, height) < 0.12 ? 'point' : undefined}
            style={{
              left: `${(x + width / 2) * 100}%`,
              top: `${(y + height / 2) * 100}%`,
              width: `${width * 100}%`,
              height: `${height * 100}%`,
            }}
          />
        ))}
      </div>
    </aside>
  );
}
