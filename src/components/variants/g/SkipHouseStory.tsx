import type { MouseEvent } from 'react';

export default function SkipHouseStory({
  staticView = false,
}: {
  staticView?: boolean;
}) {
  const skip = (event: MouseEvent<HTMLAnchorElement>) => {
    if (
      event.button !== 0 ||
      event.metaKey ||
      event.ctrlKey ||
      event.shiftKey ||
      event.altKey
    )
      return;
    const projects = document.getElementById('projekte');
    if (!projects) return;
    event.preventDefault();
    projects.scrollIntoView({ behavior: 'instant', block: 'start' });
    document.getElementById('g-projects-title')?.focus({ preventScroll: true });
    if (window.location.hash !== '#projekte') {
      window.history.pushState(window.history.state, '', '#projekte');
    }
  };

  return (
    <a className="g-house-skip" href="#projekte" onClick={skip}>
      <span>
        {staticView ? 'Direkt zu den Projekten' : 'Animation überspringen'}
      </span>
      <span aria-hidden="true">↓</span>
    </a>
  );
}
