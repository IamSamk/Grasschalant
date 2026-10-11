/**
 * Grasschalant — Main Application
 * 
 * Responsive routing between mobile capture HUD and desktop storybook viewer.
 * Detects device type and shows appropriate view.
 */

import { useState } from 'react';
import MobilePedometerHUD from './views/mobile/MobilePedometerHUD';
import StoryBookViewer from './views/desktop/StoryBookViewer';
import {
  BookOpen,
  Footprints,
  Sparkles,
  List,
  Plus,
  Eye,
} from 'lucide-react';
import './index.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type AppView = 'home' | 'capture' | 'book' | 'gallery';

interface OutingSummary {
  id: string;
  goal_steps: number;
  total_photos_target: number;
  current_steps: number;
  pages_count: number;
  started_at: string;
  status: string;
}

function App() {
  const [view, setView] = useState<AppView>('home');
  const [selectedOutingId, setSelectedOutingId] = useState<string>('');
  const [outings, setOutings] = useState<OutingSummary[]>([]);
  const [loadingOutings, setLoadingOutings] = useState(false);

  // Fetch past outings for gallery view
  const fetchOutings = async () => {
    setLoadingOutings(true);
    try {
      const res = await fetch(`${API_BASE}/api/outings`);
      if (res.ok) {
        const data = await res.json();
        setOutings(data);
      }
    } catch (err) {
      console.error('[App] Failed to fetch outings:', err);
    } finally {
      setLoadingOutings(false);
    }
  };

  const handleOutingComplete = (outingId: string) => {
    setSelectedOutingId(outingId);
    setView('book');
  };

  const handleViewBook = (outingId: string) => {
    setSelectedOutingId(outingId);
    setView('book');
  };

  // ─── HOME VIEW ─────────────────────────────────────────────────────────
  if (view === 'home') {
    return (
      <div className="app-container">
        <div className="home-screen">
          {/* Hero section */}
          <div className="home-hero">
            <div className="home-hero-bg" />
            <div className="home-hero-content">
              <div className="home-logo">
                <div className="home-logo-icon">
                  <Sparkles size={40} />
                </div>
                <h1 className="home-title">Grasschalant</h1>
                <p className="home-subtitle">Touch Grass Edition 🌿</p>
              </div>

              <p className="home-description">
                Walk outdoors, capture the world around you, and discover
                hidden memes in everyday objects. Your journey becomes an
                interactive storybook.
              </p>
            </div>
          </div>

          {/* Action cards */}
          <div className="home-actions">
            <button className="home-card home-card-primary" onClick={() => setView('capture')}>
              <div className="home-card-icon">
                <Plus size={28} />
              </div>
              <div className="home-card-text">
                <h3>New Expedition</h3>
                <p>Set a step goal and start exploring</p>
              </div>
              <Footprints size={64} className="home-card-bg-icon" />
            </button>

            <button
              className="home-card home-card-secondary"
              onClick={() => {
                fetchOutings();
                setView('gallery');
              }}
            >
              <div className="home-card-icon">
                <BookOpen size={28} />
              </div>
              <div className="home-card-text">
                <h3>My Storybooks</h3>
                <p>View past adventures</p>
              </div>
              <List size={64} className="home-card-bg-icon" />
            </button>
          </div>

          {/* Tech badges */}
          <div className="home-tech">
            <span className="tech-badge">PaliGemma AI</span>
            <span className="tech-badge">MongoDB Atlas</span>
            <span className="tech-badge">Vector Search</span>
            <span className="tech-badge">Cloudinary CDN</span>
          </div>
        </div>
      </div>
    );
  }

  // ─── CAPTURE VIEW ──────────────────────────────────────────────────────
  if (view === 'capture') {
    return (
      <div className="app-container">
        <MobilePedometerHUD onComplete={handleOutingComplete} />
      </div>
    );
  }

  // ─── BOOK VIEW ─────────────────────────────────────────────────────────
  if (view === 'book' && selectedOutingId) {
    return (
      <div className="app-container">
        <StoryBookViewer
          outingId={selectedOutingId}
          onBack={() => setView('home')}
        />
      </div>
    );
  }

  // ─── GALLERY VIEW ─────────────────────────────────────────────────────
  if (view === 'gallery') {
    return (
      <div className="app-container">
        <div className="gallery-screen">
          <div className="gallery-header">
            <button className="gallery-back" onClick={() => setView('home')}>
              ← Back
            </button>
            <h2>My Storybooks</h2>
          </div>

          {loadingOutings && (
            <div className="gallery-loading">
              <div className="loader" />
              <p>Loading your adventures...</p>
            </div>
          )}

          {!loadingOutings && outings.length === 0 && (
            <div className="gallery-empty">
              <BookOpen size={48} />
              <p>No adventures yet!</p>
              <button className="gallery-start-btn" onClick={() => setView('capture')}>
                Start Your First Expedition
              </button>
            </div>
          )}

          <div className="gallery-grid">
            {outings.map(outing => (
              <button
                key={outing.id}
                className="gallery-card"
                onClick={() => handleViewBook(outing.id)}
              >
                <div className="gallery-card-header">
                  <span className={`gallery-status ${outing.status}`}>
                    {outing.status === 'completed' ? '✅' : '🚶'}
                    {outing.status}
                  </span>
                  <span className="gallery-date">
                    {new Date(outing.started_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </span>
                </div>
                <div className="gallery-card-stats">
                  <div className="gallery-stat">
                    <Footprints size={16} />
                    <span>{outing.current_steps.toLocaleString()} steps</span>
                  </div>
                  <div className="gallery-stat">
                    <Eye size={16} />
                    <span>{outing.pages_count} photos</span>
                  </div>
                </div>
                <div className="gallery-card-action">
                  <BookOpen size={16} />
                  <span>View Storybook</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
}

export default App;
