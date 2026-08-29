import { Canvas, useFrame } from '@react-three/fiber';
import { Line, OrbitControls } from '@react-three/drei';
import { useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';

export type HouseStoryState =
  'planning' | 'installation' | 'energy' | 'service';

type StoryChapter = {
  id: HouseStoryState;
  number: string;
  label: string;
  title: string;
  description: string;
  cta?: string;
  href?: string;
  hint: string;
  callouts?: string[];
};

const chapters: StoryChapter[] = [
  {
    id: 'planning',
    number: '01',
    label: 'Planung',
    title: 'Ein Haus beginnt mit einem guten Plan.',
    description:
      'Wir planen die komplette Elektrotechnik für Neubau, Sanierung und Gewerbe.',
    cta: 'Projekt besprechen →',
    href: '#projektanfrage',
    hint: 'Scrollen, um das Haus zu entdecken',
  },
  {
    id: 'installation',
    number: '02',
    label: 'Installation',
    title: 'Im Inneren greift alles ineinander.',
    description:
      'Elektroinstallation, Beleuchtung, Netzwerk und Gebäudetechnik – sauber geplant und umgesetzt.',
    hint: 'Weiter zum Dach',
    callouts: [
      'Elektroinstallation',
      'Beleuchtung & KNX',
      'Netzwerk & Sicherheit',
    ],
  },
  {
    id: 'energy',
    number: '03',
    label: 'Energie',
    title: 'Auf dem Dach wird das Haus zum Energieerzeuger.',
    description:
      'Photovoltaik, Speicher und elektrische Einbindung – als durchdachtes Gesamtsystem.',
    cta: 'Photovoltaik anfragen →',
    href: '#projektanfrage',
    hint: 'Weiter zur Prüfung & Übergabe',
    callouts: ['Photovoltaik', 'Speicher & Einspeisung'],
  },
  {
    id: 'service',
    number: '04',
    label: 'Service',
    title: 'Geprüft. Dokumentiert. Übergeben.',
    description:
      'Wir begleiten das Projekt von der ersten Planung bis zur fachgerechten Übergabe und stehen auch danach für Service und Überprüfungen zur Verfügung.',
    cta: 'Projekt anfragen →',
    href: '#projektanfrage',
    hint: 'Das fertige Haus',
  },
];

export function getStoryState(progress: number): HouseStoryState {
  if (progress < 0.25) return 'planning';
  if (progress < 0.52) return 'installation';
  if (progress < 0.78) return 'energy';
  return 'service';
}

function stateIndex(state: HouseStoryState) {
  return chapters.findIndex((chapter) => chapter.id === state);
}

function Materials() {
  return null;
}

function GableRoof() {
  const geometry = useMemo(() => {
    const profile = new THREE.Shape();
    profile.moveTo(-3.48, 2.12);
    profile.lineTo(0, 4.02);
    profile.lineTo(3.48, 2.12);
    profile.closePath();
    const roof = new THREE.ExtrudeGeometry(profile, {
      depth: 4.7,
      bevelEnabled: false,
    });
    roof.translate(0, 0, -2.35);
    return roof;
  }, []);
  return (
    <mesh geometry={geometry} castShadow receiveShadow>
      <meshStandardMaterial color="#303234" roughness={0.82} />
    </mesh>
  );
}

function Window({
  position,
  rotation = [0, 0, 0],
  size = [1.25, 1.45],
}: {
  position: [number, number, number];
  rotation?: [number, number, number];
  size?: [number, number];
}) {
  return (
    <group position={position} rotation={rotation}>
      <mesh>
        <boxGeometry args={[size[0], size[1], 0.08]} />
        <meshStandardMaterial
          color="#263034"
          roughness={0.35}
          metalness={0.25}
        />
      </mesh>
      <mesh position={[0, 0, 0.05]}>
        <boxGeometry args={[size[0] - 0.12, size[1] - 0.12, 0.03]} />
        <meshPhysicalMaterial
          color="#9bb0b6"
          transparent
          opacity={0.42}
          roughness={0.1}
          metalness={0.05}
        />
      </mesh>
    </group>
  );
}

function SolarPanel({
  position,
  rotation,
  visible,
}: {
  position: [number, number, number];
  rotation: [number, number, number];
  visible: number;
}) {
  const ref = useRef<THREE.Group>(null);
  useFrame(() => {
    if (!ref.current) return;
    ref.current.scale.setScalar(
      THREE.MathUtils.lerp(ref.current.scale.x, visible, 0.08),
    );
    ref.current.position.y = THREE.MathUtils.lerp(
      ref.current.position.y,
      position[1] + (1 - visible) * 0.8,
      0.08,
    );
  });
  return (
    <group ref={ref} position={position} rotation={rotation} scale={visible}>
      <mesh castShadow>
        <boxGeometry args={[1.1, 0.06, 0.72]} />
        <meshStandardMaterial
          color="#17252c"
          metalness={0.55}
          roughness={0.25}
        />
      </mesh>
      <mesh position={[0, 0.034, 0]}>
        <boxGeometry args={[1.04, 0.008, 0.66]} />
        <meshStandardMaterial
          color="#274955"
          metalness={0.45}
          roughness={0.2}
        />
      </mesh>
    </group>
  );
}

function HouseModel({
  state,
  staticMode = false,
}: {
  state: HouseStoryState;
  staticMode?: boolean;
}) {
  const shell = useRef<THREE.Group>(null);
  const interior = useRef<THREE.Group>(null);
  const energy = useRef<THREE.Group>(null);
  const serviceLights = useRef<THREE.Group>(null);
  const installationVisible = state === 'installation';
  const energyVisible = state === 'energy' || state === 'service';
  const serviceVisible = state === 'service';
  const redLinePoints = useMemo(
    () => [
      new THREE.Vector3(3.45, -1.7, 1.72),
      new THREE.Vector3(3.45, -0.65, 1.72),
      new THREE.Vector3(2.6, -0.25, 1.72),
      new THREE.Vector3(1.8, 0.35, 1.72),
      new THREE.Vector3(0.4, 0.35, 1.72),
      new THREE.Vector3(-0.9, 1.25, 1.72),
      new THREE.Vector3(-1.8, 2.55, 0.3),
    ],
    [],
  );

  useFrame(() => {
    if (staticMode) return;
    const cut = installationVisible ? 0 : 1;
    if (shell.current) {
      shell.current.position.z = THREE.MathUtils.lerp(
        shell.current.position.z,
        cut ? 0 : -0.65,
        0.07,
      );
      shell.current.rotation.y = THREE.MathUtils.lerp(
        shell.current.rotation.y,
        cut ? 0 : -0.035,
        0.07,
      );
    }
    if (interior.current) {
      interior.current.scale.setScalar(
        THREE.MathUtils.lerp(
          interior.current.scale.x,
          installationVisible ? 1 : 0.001,
          0.08,
        ),
      );
    }
    if (energy.current) {
      energy.current.scale.setScalar(
        THREE.MathUtils.lerp(
          energy.current.scale.x,
          energyVisible ? 1 : 0.001,
          0.07,
        ),
      );
    }
    if (serviceLights.current) {
      serviceLights.current.scale.setScalar(
        THREE.MathUtils.lerp(
          serviceLights.current.scale.x,
          serviceVisible ? 1 : 0.001,
          0.08,
        ),
      );
    }
  });

  const staticCut = staticMode && installationVisible;
  return (
    <group rotation={[0, -0.15, 0]} position={[0, -0.45, 0]}>
      <Materials />
      <mesh receiveShadow position={[0, -1.64, 0]}>
        <boxGeometry args={[18, 0.08, 18]} />
        <shadowMaterial transparent opacity={0.14} />
      </mesh>
      <mesh receiveShadow position={[0, -1.47, 0]}>
        <boxGeometry args={[7.5, 0.25, 5.15]} />
        <meshStandardMaterial color="#d8d5cf" roughness={0.9} />
      </mesh>
      <mesh receiveShadow position={[0, -1.31, 0]}>
        <boxGeometry args={[6.85, 0.14, 4.55]} />
        <meshStandardMaterial color="#bcb9b2" roughness={0.95} />
      </mesh>

      <group ref={shell} position={staticCut ? [0, 0, -0.65] : [0, 0, 0]}>
        <mesh castShadow receiveShadow position={[0, -0.35, -2.05]}>
          <boxGeometry args={[6.4, 2.15, 0.22]} />
          <meshStandardMaterial color="#f2f1ed" roughness={0.8} />
        </mesh>
        <mesh castShadow receiveShadow position={[-3.08, -0.35, 0]}>
          <boxGeometry args={[0.22, 2.15, 4.15]} />
          <meshStandardMaterial color="#eeece7" roughness={0.82} />
        </mesh>
        {!installationVisible && (
          <mesh castShadow receiveShadow position={[0, -0.35, 2.05]}>
            <boxGeometry args={[6.4, 2.15, 0.22]} />
            <meshStandardMaterial color="#f5f4f0" roughness={0.82} />
          </mesh>
        )}
        {!installationVisible && (
          <mesh castShadow receiveShadow position={[3.08, -0.35, 0]}>
            <boxGeometry args={[0.22, 2.15, 4.15]} />
            <meshStandardMaterial color="#eeeae4" roughness={0.82} />
          </mesh>
        )}
        <mesh castShadow receiveShadow position={[0, 0.78, 0.16]}>
          <boxGeometry args={[7.05, 0.22, 4.95]} />
          <meshStandardMaterial color="#b9b7b1" roughness={0.95} />
        </mesh>
        {!installationVisible && (
          <>
            <mesh castShadow position={[-2.9, -0.18, 2.3]}>
              <boxGeometry args={[0.22, 1.9, 0.22]} />
              <meshStandardMaterial color="#b9b7b1" roughness={0.95} />
            </mesh>
            <mesh castShadow position={[2.9, -0.18, 2.3]}>
              <boxGeometry args={[0.22, 1.9, 0.22]} />
              <meshStandardMaterial color="#b9b7b1" roughness={0.95} />
            </mesh>
          </>
        )}
        <mesh castShadow receiveShadow position={[0, 1.52, -2.05]}>
          <boxGeometry args={[6.4, 1.35, 0.22]} />
          <meshStandardMaterial color="#f4f3ef" roughness={0.8} />
        </mesh>
        <mesh castShadow receiveShadow position={[-3.08, 1.52, 0]}>
          <boxGeometry args={[0.22, 1.35, 4.15]} />
          <meshStandardMaterial color="#f0eee9" roughness={0.8} />
        </mesh>
        {!installationVisible && (
          <mesh castShadow receiveShadow position={[0, 1.52, 2.05]}>
            <boxGeometry args={[6.4, 1.35, 0.22]} />
            <meshStandardMaterial color="#f6f5f2" roughness={0.8} />
          </mesh>
        )}
        {!installationVisible && (
          <mesh castShadow receiveShadow position={[3.08, 1.52, 0]}>
            <boxGeometry args={[0.22, 1.35, 4.15]} />
            <meshStandardMaterial color="#f0eee8" roughness={0.8} />
          </mesh>
        )}
        {!installationVisible && <GableRoof />}
        {!installationVisible && (
          <group position={[0, 0, 2.18]}>
            <Window position={[-1.75, -0.35, 0]} size={[1.35, 1.65]} />
            <Window position={[1.68, -0.35, 0]} size={[1.55, 1.65]} />
            <Window position={[-1.75, 1.47, 0]} size={[1.35, 1.18]} />
            <Window position={[1.68, 1.47, 0]} size={[1.55, 1.18]} />
          </group>
        )}
        {!installationVisible && (
          <group position={[3.19, 0, 0]} rotation={[0, Math.PI / 2, 0]}>
            <Window position={[0, -0.35, -0.85]} size={[1.1, 1.55]} />
            <Window position={[0, 1.47, 0.75]} size={[1.1, 1.1]} />
          </group>
        )}
        {!installationVisible &&
          [-1.9, -1.52, -1.14, -0.76, -0.38, 0, 0.38].map((x) => (
            <mesh key={x} castShadow position={[x, 0.65, 2.31]}>
              <boxGeometry args={[0.16, 3.15, 0.13]} />
              <meshStandardMaterial color="#9a6745" roughness={0.75} />
            </mesh>
          ))}
      </group>

      <group
        ref={interior}
        scale={staticCut ? 1 : installationVisible ? 1 : 0.001}
      >
        <mesh position={[0, -0.35, 0]} receiveShadow>
          <boxGeometry args={[0.12, 2, 3.8]} />
          <meshStandardMaterial color="#d9d6cf" roughness={0.9} />
        </mesh>
        <mesh position={[-1.5, 1.45, 0]} receiveShadow>
          <boxGeometry args={[0.12, 1.25, 3.8]} />
          <meshStandardMaterial color="#dedbd5" roughness={0.9} />
        </mesh>
        <mesh position={[2.72, -0.2, 1.83]} castShadow>
          <boxGeometry args={[0.56, 1.15, 0.22]} />
          <meshStandardMaterial
            color="#e7e6e2"
            metalness={0.2}
            roughness={0.55}
          />
        </mesh>
        {[
          [-2, 0.65, 1.2],
          [0.8, 0.65, 0.8],
          [1.3, 2.12, 0.2],
        ].map((position, index) => (
          <group key={index} position={position as [number, number, number]}>
            <mesh>
              <cylinderGeometry args={[0.16, 0.16, 0.05, 24]} />
              <meshStandardMaterial color="#272727" />
            </mesh>
            <pointLight color="#fff2d2" intensity={2.1} distance={2.8} />
          </group>
        ))}
        <Line
          points={redLinePoints.slice(0, state === 'installation' ? 6 : 2)}
          color="#e30613"
          lineWidth={3}
        />
        <mesh position={[-1.45, 0.15, 1.72]}>
          <boxGeometry args={[0.24, 0.24, 0.1]} />
          <meshStandardMaterial color="#e30613" />
        </mesh>
        <mesh position={[1.6, 1.05, 1.72]}>
          <boxGeometry args={[0.3, 0.18, 0.1]} />
          <meshStandardMaterial color="#222" />
        </mesh>
      </group>

      <group ref={energy} scale={energyVisible ? 1 : 0.001}>
        {[-1.55, -0.35, 0.85, 2.05].flatMap((x) =>
          [-0.8, 0.05, 0.9].map((z) => (
            <SolarPanel
              key={`${x}-${z}`}
              position={[x, 4.08 - Math.abs(x) * 0.546, z]}
              rotation={[0, 0, x < 0 ? 0.5 : -0.5]}
              visible={energyVisible ? 1 : 0.001}
            />
          )),
        )}
        <mesh position={[2.66, -0.42, -1.82]}>
          <boxGeometry args={[0.58, 0.85, 0.18]} />
          <meshStandardMaterial color="#f3f2ef" roughness={0.45} />
        </mesh>
        <mesh position={[1.82, -0.52, -1.82]}>
          <boxGeometry args={[0.66, 1.25, 0.34]} />
          <meshStandardMaterial color="#e7e5df" roughness={0.5} />
        </mesh>
        <Line points={redLinePoints} color="#e30613" lineWidth={3} />
      </group>

      <group ref={serviceLights} scale={serviceVisible ? 1 : 0.001}>
        <pointLight
          position={[-1.6, 0.2, 1.5]}
          color="#fff0ce"
          intensity={4}
          distance={4}
        />
        <pointLight
          position={[1.7, 1.5, 1.5]}
          color="#fff0ce"
          intensity={3}
          distance={3}
        />
      </group>
      {(state === 'planning' || state === 'service') && (
        <Line
          points={[
            new THREE.Vector3(3.05, -1.15, 2.2),
            new THREE.Vector3(3.05, -2.05, 2.2),
            new THREE.Vector3(2.45, -2.7, 2.2),
          ]}
          color="#e30613"
          lineWidth={3}
        />
      )}
    </group>
  );
}

function CameraRig({
  state,
  staticMode,
}: {
  state: HouseStoryState;
  staticMode?: boolean;
}) {
  const targets: Record<
    HouseStoryState,
    { p: [number, number, number]; look: [number, number, number] }
  > = {
    planning: { p: [13.5, 7.5, 16], look: [0, 0.45, 0] },
    installation: { p: [10.8, 4.5, 11.5], look: [0.3, 0.45, 0] },
    energy: { p: [10, 9.4, 11], look: [0, 2.25, 0] },
    service: { p: [13.5, 7.5, 16], look: [0, 0.55, 0] },
  };
  const look = useMemo(() => new THREE.Vector3(), []);
  useFrame(({ camera }) => {
    const target = targets[state];
    if (staticMode) {
      camera.position.set(...target.p);
      camera.lookAt(...target.look);
      return;
    }
    camera.position.lerp(new THREE.Vector3(...target.p), 0.055);
    look.lerp(new THREE.Vector3(...target.look), 0.065);
    camera.lookAt(look);
  });
  return null;
}

function HouseCanvas({
  state,
  staticMode = false,
  labelledBy,
}: {
  state: HouseStoryState;
  staticMode?: boolean;
  labelledBy?: string;
}) {
  return (
    <Canvas
      aria-hidden="true"
      aria-labelledby={labelledBy}
      className="g-house-canvas"
      shadows={!staticMode}
      dpr={staticMode ? 1 : [1, 1.5]}
      frameloop={staticMode ? 'demand' : 'always'}
      camera={{ fov: 31, near: 0.1, far: 100, position: [13.5, 7.5, 16] }}
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
    >
      <color attach="background" args={['#ffffff']} />
      <ambientLight intensity={1.6} />
      <directionalLight
        castShadow={!staticMode}
        position={[8, 12, 9]}
        intensity={2.4}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
      />
      <HouseModel state={state} staticMode={staticMode} />
      <CameraRig state={state} staticMode={staticMode} />
      {staticMode && <OrbitControls enabled={false} />}
    </Canvas>
  );
}

function ChapterContent({
  chapter,
  active,
}: {
  chapter: StoryChapter;
  active: boolean;
}) {
  return (
    <article
      className={`g-story-copy ${active ? 'is-active' : ''}`}
      aria-hidden={!active}
    >
      <p className="g-eyebrow">
        <strong>{chapter.number}</strong> · {chapter.label}
      </p>
      <h2 id={`g-title-${chapter.id}`}>{chapter.title}</h2>
      <p className="g-story-description">{chapter.description}</p>
      {chapter.callouts && (
        <ul className="g-callouts">
          {chapter.callouts.map((callout) => (
            <li key={callout}>{callout}</li>
          ))}
        </ul>
      )}
      {chapter.cta && chapter.href && (
        <a className="g-outline-button" href={chapter.href}>
          {chapter.cta}
        </a>
      )}
      <span className="g-scroll-hint">
        {chapter.hint}
        <i aria-hidden="true">↓</i>
      </span>
    </article>
  );
}

export default function HouseStory() {
  const wrapper = useRef<HTMLElement>(null);
  const [state, setState] = useState<HouseStoryState>('planning');

  useEffect(() => {
    let frame = 0;
    const update = () => {
      frame = 0;
      if (!wrapper.current) return;
      const rect = wrapper.current.getBoundingClientRect();
      const scrollable = wrapper.current.offsetHeight - window.innerHeight;
      const next = THREE.MathUtils.clamp(
        -rect.top / Math.max(scrollable, 1),
        0,
        1,
      );
      setState(getStoryState(next));
    };
    const onScroll = () => {
      if (!frame) frame = window.requestAnimationFrame(update);
    };
    update();
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', onScroll);
      window.removeEventListener('resize', onScroll);
      if (frame) window.cancelAnimationFrame(frame);
    };
  }, []);
  const activeIndex = stateIndex(state);
  return (
    <section
      ref={wrapper}
      className="g-story"
      aria-label="Leistungen von der Planung bis zur Übergabe"
    >
      <div className="g-story-stage">
        <div className="g-story-canvas-wrap">
          <HouseCanvas state={state} labelledBy={`g-title-${state}`} />
        </div>
        <div className="g-story-copy-stack">
          {chapters.map((chapter) => (
            <ChapterContent
              key={chapter.id}
              chapter={chapter}
              active={chapter.id === state}
            />
          ))}
        </div>
        <nav className="g-progress" aria-label="Fortschritt der Haus-Story">
          <strong>
            <span>{chapters[activeIndex]?.number}</span> / 04
          </strong>
          <ol>
            {chapters.map((chapter) => (
              <li
                className={chapter.id === state ? 'is-active' : ''}
                key={chapter.id}
              >
                <span>{chapter.label}</span>
              </li>
            ))}
          </ol>
        </nav>
      </div>
    </section>
  );
}
