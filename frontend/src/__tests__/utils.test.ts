import { describe, it, expect } from 'vitest';
import { formatBytes, formatDate } from '../utils/cn';

describe('Frontend Formatting Utilities', () => {
  it('formats byte sizes correctly', () => {
    expect(formatBytes(0)).toBe('0 B');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
    expect(formatBytes(20971520)).toBe('20 MB');
  });

  it('formats dates consistently', () => {
    const dateStr = '2026-11-20T20:00:00Z';
    const formatted = formatDate(dateStr);
    expect(formatted).toContain('2026');
  });
});
