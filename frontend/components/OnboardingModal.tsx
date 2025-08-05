import { getThemePreviews, useTheme } from '../themeEngine';
import { useEffect } from 'react';

type Props = { onClose: () => void };

export default function OnboardingModal({ onClose }: Props) {
  const { switchTheme } = useTheme();
  const themes = getThemePreviews();

  const handleSelect = async (name: string) => {
    await switchTheme(name);
    onClose();
  };

  useEffect(() => {
    // Block background scroll
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-white p-4 rounded shadow-md w-80">
        <h2 className="mb-2">Select Palette</h2>
        <div className="grid grid-cols-2 gap-2">
          {themes.map(t => (
            <button key={t.name} onClick={() => handleSelect(t.name)}
              style={{background: t.colors[0], color: '#fff', padding: '8px', borderRadius: '4px'}}>
              {t.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
