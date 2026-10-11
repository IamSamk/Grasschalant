/**
 * StoryBookViewer — Interactive 3D Day Out Storybook
 * 
 * Dual-page flip book with:
 * - CSS 3D transforms for realistic page flipping
 * - Cover page with expedition summary
 * - Left pages: outdoor photo + step badge + literal description
 * - Right pages: matched meme + confidence badge + explanation
 * - Keyboard navigation (arrow keys)
 * - Touch/swipe support
 */

import { useState, useEffect, useCallback, useRef, type TouchEvent } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Download,
  Footprints,
  Clock,
  Camera,
  ArrowLeft,
  Sparkles,
} from 'lucide-react';
import { exportToPDF } from '../../utils/PDFExport';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Page {
  page_index: number;
  real_image_url: string;
  meme_image_url: string;
  meme_name: string;
  literal_description: string;
  meme_analogy_concept: string;
  explanation: string;
  match_confidence: number;
  step_count: number;
  timestamp: string;
}

interface Outing {
  id: string;
  goal_steps: number;
  total_photos_target: number;
  milestone_interval: number;
  current_steps: number;
  pages: Page[];
  started_at: string;
  status: string;
}

interface StoryBookViewerProps {
  outingId: string;
  onBack?: () => void;
}

export default function StoryBookViewer({ outingId, onBack }: StoryBookViewerProps) {
  const [outing, setOuting] = useState<Outing | null>(null);
  const [currentPage, setCurrentPage] = useState(0); // 0 = cover, then pairs
  const [isFlipping, setIsFlipping] = useState(false);
  const [flipDirection, setFlipDirection] = useState<'next' | 'prev'>('next');
  const [isExporting, setIsExporting] = useState(false);
  const [loading, setLoading] = useState(true);
  const bookRef = useRef<HTMLDivElement>(null);
  const touchStartX = useRef(0);

  // Total pages: cover + (n spreads) + back cover
  const totalPages = outing ? outing.pages.length + 2 : 2;

  // Fetch outing data
  useEffect(() => {
    const fetchOuting = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/outings/${outingId}`);
        if (res.ok) {
          const data = await res.json();
          setOuting(data);
        }
      } catch (err) {
        console.error('[Book] Failed to fetch outing:', err);
      } finally {
        setLoading(false);
      }
    };

    if (outingId.startsWith('offline-')) {
      // Demo mode with mock data
      setOuting({
        id: outingId,
        goal_steps: 6000,
        total_photos_target: 10,
        milestone_interval: 600,
        current_steps: 6000,
        pages: [],
        started_at: new Date().toISOString(),
        status: 'completed',
      });
      setLoading(false);
    } else {
      fetchOuting();
    }
  }, [outingId]);

  // Page navigation
  const goToPage = useCallback((page: number, direction: 'next' | 'prev') => {
    if (isFlipping || page < 0 || page >= totalPages) return;
    setIsFlipping(true);
    setFlipDirection(direction);
    setTimeout(() => {
      setCurrentPage(page);
      setIsFlipping(false);
    }, 600);
  }, [isFlipping, totalPages]);

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1, 'next');
  }, [currentPage, goToPage]);

  const prevPage = useCallback(() => {
    goToPage(currentPage - 1, 'prev');
  }, [currentPage, goToPage]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === ' ') {
        e.preventDefault();
        nextPage();
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        prevPage();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [nextPage, prevPage]);

  // Touch/swipe support
  const handleTouchStart = (e: TouchEvent) => {
    touchStartX.current = e.touches[0].clientX;
  };

  const handleTouchEnd = (e: TouchEvent) => {
    const diff = touchStartX.current - e.changedTouches[0].clientX;
    if (Math.abs(diff) > 50) {
      if (diff > 0) nextPage();
      else prevPage();
    }
  };

  // PDF export
  const handleExport = async () => {
    if (!bookRef.current || !outing) return;
    setIsExporting(true);
    try {
      await exportToPDF(outing);
    } catch (err) {
      console.error('[Book] Export failed:', err);
    } finally {
      setIsExporting(false);
    }
  };

  if (loading) {
    return (
      <div className="book-container book-loading">
        <div className="book-loader">
          <BookOpen size={48} className="book-loader-icon" />
          <p>Composing your storybook...</p>
        </div>
      </div>
    );
  }

  if (!outing) {
    return (
      <div className="book-container book-error">
        <p>Outing not found</p>
        {onBack && (
          <button onClick={onBack} className="book-btn-back">
            <ArrowLeft size={16} /> Go Back
          </button>
        )}
      </div>
    );
  }

  const startDate = new Date(outing.started_at);

  // ─── Render current page content ─────────────────────────────────────
  const renderPageContent = () => {
    // Cover page
    if (currentPage === 0) {
      return (
        <div className="book-spread book-cover">
          <div className="book-page book-page-full">
            <div className="book-cover-content">
              <div className="book-cover-decoration">
                <Sparkles size={32} />
              </div>
              <h1 className="book-cover-title">My Touch Grass Expedition</h1>
              <div className="book-cover-divider" />
              <div className="book-cover-stats">
                <div className="book-cover-stat">
                  <Footprints size={24} />
                  <span className="book-cover-stat-value">{outing.current_steps.toLocaleString()}</span>
                  <span className="book-cover-stat-label">Total Steps</span>
                </div>
                <div className="book-cover-stat">
                  <Camera size={24} />
                  <span className="book-cover-stat-value">{outing.pages.length}</span>
                  <span className="book-cover-stat-label">Discoveries</span>
                </div>
                <div className="book-cover-stat">
                  <Clock size={24} />
                  <span className="book-cover-stat-value">
                    {startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </span>
                  <span className="book-cover-stat-label">Date</span>
                </div>
              </div>
              <p className="book-cover-subtitle">A Grasschalant Adventure 🌿</p>
            </div>
          </div>
        </div>
      );
    }

    // Back cover
    if (currentPage >= totalPages - 1) {
      return (
        <div className="book-spread book-back-cover">
          <div className="book-page book-page-full">
            <div className="book-cover-content">
              <h2>The End</h2>
              <p className="book-back-message">
                You walked <strong>{outing.current_steps.toLocaleString()}</strong> steps,
                discovered <strong>{outing.pages.length}</strong> hidden memes in the wild,
                and lived to tell the tale.
              </p>
              <p className="book-back-tagline">Made with 🌿 by Grasschalant</p>
            </div>
          </div>
        </div>
      );
    }

    // Content spread (left: photo, right: meme)
    const pageIndex = currentPage - 1;
    const page = outing.pages[pageIndex];

    if (!page) return null;

    return (
      <div className="book-spread">
        {/* Left page — Real outdoor photo */}
        <div className="book-page book-page-left">
          <div className="book-page-inner">
            <div className="book-photo-frame">
              <img
                src={page.real_image_url}
                alt={page.literal_description}
                className="book-photo"
                crossOrigin="anonymous"
              />
            </div>
            <div className="book-page-meta">
              <div className="book-step-badge">
                <Footprints size={14} />
                <span>Discovered at Step {page.step_count.toLocaleString()}</span>
              </div>
              <p className="book-description">{page.literal_description}</p>
              <span className="book-page-number">{pageIndex * 2 + 1}</span>
            </div>
          </div>
        </div>

        {/* Right page — Matching meme */}
        <div className="book-page book-page-right">
          <div className="book-page-inner">
            <div className="book-meme-frame">
              <img
                src={page.meme_image_url}
                alt={page.meme_name}
                className="book-meme"
                crossOrigin="anonymous"
              />
            </div>
            <div className="book-page-meta">
              <div className="book-match-badge">
                <Sparkles size={14} />
                <span>{Math.round(page.match_confidence * 100)}% Match</span>
              </div>
              <h3 className="book-meme-name">{page.meme_name}</h3>
              <p className="book-explanation">{page.explanation}</p>
              <span className="book-page-number">{pageIndex * 2 + 2}</span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="book-container" ref={bookRef}>
      {/* Toolbar */}
      <div className="book-toolbar">
        {onBack && (
          <button onClick={onBack} className="book-toolbar-btn">
            <ArrowLeft size={18} />
            <span>Back</span>
          </button>
        )}
        <div className="book-toolbar-center">
          <span className="book-page-indicator">
            {currentPage + 1} / {totalPages}
          </span>
        </div>
        <button
          onClick={handleExport}
          className="book-toolbar-btn book-export-btn"
          disabled={isExporting}
        >
          <Download size={18} />
          <span>{isExporting ? 'Exporting...' : 'PDF'}</span>
        </button>
      </div>

      {/* Book */}
      <div
        className={`book-frame ${isFlipping ? `flipping-${flipDirection}` : ''}`}
        onTouchStart={handleTouchStart}
        onTouchEnd={handleTouchEnd}
      >
        {renderPageContent()}
      </div>

      {/* Navigation */}
      <div className="book-nav">
        <button
          className="book-nav-btn"
          onClick={prevPage}
          disabled={currentPage === 0 || isFlipping}
        >
          <ChevronLeft size={24} />
        </button>
        <button
          className="book-nav-btn"
          onClick={nextPage}
          disabled={currentPage >= totalPages - 1 || isFlipping}
        >
          <ChevronRight size={24} />
        </button>
      </div>
    </div>
  );
}
