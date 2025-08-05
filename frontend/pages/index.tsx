import { useEffect, useState } from 'react';
import Image from 'next/image';
import { useTheme } from '../themeEngine';
import OnboardingModal from '../components/OnboardingModal';
import logo from '../assets/logo.png';
import background from '../assets/background.png';

export default function Home() {
  const { theme } = useTheme();
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem('brc_palette')) setShowModal(true);
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      backgroundImage: `url(${background.src})`,
      backgroundSize: 'cover',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center'
    }}>
      <Image src={logo} alt="Black Rose Collective" width={120} height={120} />
      <h1 style={{ color: 'var(--color-0)' }}>Black Rose Collective</h1>
      {showModal && <OnboardingModal onClose={() => setShowModal(false)} />}
    </div>
  );
}
