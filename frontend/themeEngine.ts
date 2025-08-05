import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import moodyFloral from './themes/moodyFloral';
import stormyMountain from './themes/stormyMountain';
import mutedOcean from './themes/mutedOcean';
import vintageRose from './themes/vintageRose';
import mistyPurple from './themes/mistyPurple';
import luxeSilver from './themes/luxeSilver';
import forestWhisper from './themes/forestWhisper';

export interface ThemeConfig {
  name: string;
  colors: string[];
}

const ALL_THEMES: ThemeConfig[] = [
  moodyFloral,
  stormyMountain,
  mutedOcean,
  vintageRose,
  mistyPurple,
  luxeSilver,
  forestWhisper,
];

const STORAGE_KEY = 'brc_palette';

function applyColors(colors: string[]) {
  const root = document.documentElement;
  colors.forEach((color, idx) => {
    root.style.setProperty(`--color-${idx}`, color);
  });
}

function hasAccess(name: string): boolean {
  const key = `brc_theme_owned_${name}`;
  return localStorage.getItem(key) === 'true' || name === 'Moody Floral';
}

async function purchaseTheme(name: string): Promise<boolean> {
  const res = await fetch('/api/purchase-theme', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ theme: name }),
  });
  if (res.ok) {
    const key = `brc_theme_owned_${name}`;
    localStorage.setItem(key, 'true');
    return true;
  }
  return false;
}

type ThemeContextValue = {
  theme: ThemeConfig;
  themes: ThemeConfig[];
  switchTheme: (name: string) => Promise<void>;
};

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<ThemeConfig>(moodyFloral);

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const found = ALL_THEMES.find(t => t.name === saved);
    if (found) {
      setTheme(found);
      applyColors(found.colors);
    } else {
      applyColors(moodyFloral.colors);
    }
  }, []);

  const switchTheme = async (name: string) => {
    const target = ALL_THEMES.find(t => t.name === name);
    if (!target) return;
    if (!hasAccess(name)) {
      const purchased = await purchaseTheme(name);
      if (!purchased) return;
    }
    applyColors(target.colors);
    localStorage.setItem(STORAGE_KEY, name);
    setTheme(target);
  };

  return React.createElement(ThemeContext.Provider, { value: { theme, themes: ALL_THEMES, switchTheme } }, children);
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider');
  return ctx;
}

export function getThemePreviews(): ThemeConfig[] {
  return ALL_THEMES;
}
