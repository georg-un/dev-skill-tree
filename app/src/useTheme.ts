// useTheme.ts
import { useState, useEffect, useMemo } from 'react';

interface Theme {
  text: string;
  background: string;
  primary: string;
  secondary: string;
  accent: string;
  isDarkMode: boolean;
}

export function useTheme(): Theme {
  const [isDarkMode, setIsDarkMode] = useState(
    window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handler = (e: MediaQueryListEvent) => setIsDarkMode(e.matches);

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  const colors = useMemo<Omit<Theme, 'isDarkMode'>>(() => {
    const root = document.documentElement;
    const getColor = (variable: string) => getComputedStyle(root).getPropertyValue(variable).trim();

    return {
      text: getColor('--text'),
      background: getColor('--background'),
      primary: getColor('--primary'),
      secondary: getColor('--secondary'),
      accent: getColor('--accent'),
    };
  }, [isDarkMode]);

  return { ...colors, isDarkMode };
}
