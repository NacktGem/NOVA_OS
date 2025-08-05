import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useTheme } from '../themeEngine';

const BG_MAP: Record<string, string> = {
  '/': '/assets/black_rose_home.png',
  '/404': '/assets/black_rose_404.png',
};

function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function createOverlay(colors: string[]): string {
  const start = hexToRgba(colors[0], 0.85);
  const end = hexToRgba(colors[1] ?? colors[0], 0.85);
  return `linear-gradient(135deg, ${start}, ${end})`;
}

export default function BrandBackground() {
  const { theme } = useTheme();
  const router = useRouter();

  const getSrc = () => BG_MAP[router.pathname] || '/assets/black_rose_dark.png';

  const [bg, setBg] = useState({ src: getSrc(), overlay: createOverlay(theme.colors) });
  const [visible, setVisible] = useState(true);

  useEffect(() => {
    const nextSrc = getSrc();
    const nextOverlay = createOverlay(theme.colors);
    if (nextSrc === bg.src && nextOverlay === bg.overlay) return;

    setVisible(false);
    const id = setTimeout(() => {
      setBg({ src: nextSrc, overlay: nextOverlay });
      setVisible(true);
    }, 300);
    return () => clearTimeout(id);
  }, [router.pathname, theme]);

  return (
    <div className="brand-bg">
      <div
        className="brand-bg-image"
        style={{
          backgroundImage: `url(${bg.src})`,
          opacity: visible ? 1 : 0,
        }}
      >
        <div className="brand-bg-overlay" style={{ background: bg.overlay }} />
        <div className="brand-bg-texture" />
      </div>
    </div>
  );
}
