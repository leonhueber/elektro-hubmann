import {
  IconClipboardCheck,
  IconCrane,
  IconNetwork,
  IconShieldCheck,
  IconSolarPanel,
} from '@tabler/icons-react';

const icons = {
  '01': IconCrane,
  '02': IconSolarPanel,
  '03': IconShieldCheck,
  '04': IconNetwork,
  '05': IconClipboardCheck,
} as const;

interface Props {
  kind: keyof typeof icons;
}

export default function ServiceIcon({ kind }: Props) {
  const Icon = icons[kind];

  return (
    <Icon
      className="service-showcase__icon"
      size={36}
      stroke={1.45}
      aria-hidden="true"
    />
  );
}
