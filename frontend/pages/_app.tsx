import type { AppProps } from 'next/app';
import { ThemeProvider } from '../themeEngine';
import BrandBackground from '../components/BrandBackground';
import '../styles.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <BrandBackground />
      <Component {...pageProps} />
    </ThemeProvider>
  );
}
