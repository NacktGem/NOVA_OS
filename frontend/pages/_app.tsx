import type { AppProps } from 'next/app';
import { ThemeProvider } from '../themeEngine';
import '../styles.css';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider>
      <Component {...pageProps} />
    </ThemeProvider>
  );
}
