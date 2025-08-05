import { useEffect, useState } from 'react';
import OnboardingModal from '../components/OnboardingModal';

export default function Home() {
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem('brc_palette')) setShowModal(true);
  }, []);

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <img src="/assets/logo.png" alt="Black Rose Collective" width={120} height={120} />
      <h1 style={{ color: 'var(--color-0)' }}>Black Rose Collective</h1>
      {showModal && <OnboardingModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
