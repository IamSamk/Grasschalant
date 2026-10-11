/**
 * MobilePedometerHUD — Touch-first outdoor exploration interface
 * 
 * Viewport-locked mobile HUD with:
 * - Circular SVG progress ring (steps vs goal)
 * - Milestone unlock indicators
 * - Camera shutter button (unlocks at step milestones)
 * - Haptic feedback on milestone achievement
 * - Simulation toggle for desktop/bench testing
 */

import { useState, useEffect, useCallback } from 'react';
import { usePedometer } from '../../hooks/usePedometer';
import { useCamera } from '../../hooks/useCamera';
import {
  Footprints,
  Camera,
  Zap,
  Play,
  BookOpen,
  Plus,
  Sparkles,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface MobilePedometerHUDProps {
  onComplete?: (outingId: string) => void;
}

export default function MobilePedometerHUD({ onComplete }: MobilePedometerHUDProps) {
  const pedometer = usePedometer(6000, 10);
  const camera = useCamera();

  const [outingId, setOutingId] = useState<string | null>(null);
  const [isStarted, setIsStarted] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [lastSnap, setLastSnap] = useState<any>(null);
  const [showResult, setShowResult] = useState(false);
  const [goalInput, setGoalInput] = useState(6000);
  const [photosInput, setPhotosInput] = useState(10);
  const [pagesCount, setPagesCount] = useState(0);

  // Progress calculations
  const progress = Math.min(pedometer.steps / pedometer.goalSteps, 1);
  const circumference = 2 * Math.PI * 120;
  const strokeDashoffset = circumference * (1 - progress);

  // Haptic feedback on milestone unlock
  useEffect(() => {
    if (pedometer.canSnap && navigator.vibrate) {
      navigator.vibrate([100, 50, 100, 50, 200]);
    }
  }, [pedometer.currentMilestone]);

  // Start a new outing session
  const handleStart = useCallback(async () => {
    try {
      pedometer.setGoal(goalInput, photosInput);
      await camera.startCamera();

      const res = await fetch(`${API_BASE}/api/outings/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          goal_steps: goalInput,
          total_photos_target: photosInput,
        }),
      });

      if (!res.ok) throw new Error('Failed to start outing');

      const data = await res.json();
      setOutingId(data.id);
      setIsStarted(true);
      await pedometer.startTracking();
    } catch (err) {
      console.error('[HUD] Start failed:', err);
      // Start in offline mode anyway
      setIsStarted(true);
      setOutingId('offline-' + Date.now());
      await pedometer.startTracking();
    }
  }, [goalInput, photosInput, pedometer, camera]);

  // Capture and upload a snap
  const handleSnap = useCallback(async () => {
    if (!pedometer.canSnap || isUploading) return;

    setIsUploading(true);

    try {
      const blob = await camera.captureFrame();
      if (!blob || !outingId) {
        setIsUploading(false);
        return;
      }

      // Haptic: shutter click
      if (navigator.vibrate) navigator.vibrate(50);

      const formData = new FormData();
      formData.append('photo', blob, `snap_${pagesCount}.jpg`);
      formData.append('step_count', String(pedometer.steps));

      const res = await fetch(`${API_BASE}/api/outings/${outingId}/snap`, {
        method: 'POST',
        body: formData,
      });

      if (res.ok) {
        const snapResult = await res.json();
        setLastSnap(snapResult);
        setShowResult(true);
        pedometer.onSnap();
        setPagesCount(prev => prev + 1);

        // Auto-hide result after 4 seconds
        setTimeout(() => setShowResult(false), 4000);
      }
    } catch (err) {
      console.error('[HUD] Snap failed:', err);
    } finally {
      setIsUploading(false);
    }
  }, [pedometer, camera, outingId, isUploading, pagesCount]);

  // Finish the outing
  const handleFinish = useCallback(() => {
    pedometer.stopTracking();
    camera.stopCamera();
    if (onComplete && outingId) {
      onComplete(outingId);
    }
  }, [pedometer, camera, onComplete, outingId]);

  // ─── PRE-START SCREEN ──────────────────────────────────────────────────
  if (!isStarted) {
    return (
      <div className="hud-container hud-start">
        <div className="hud-start-content">
          <div className="hud-logo">
            <Sparkles size={48} />
            <h1>Grasschalant</h1>
            <p className="hud-tagline">Touch Grass Edition 🌿</p>
          </div>

          <div className="hud-setup">
            <div className="hud-input-group">
              <label>
                <Footprints size={16} />
                Step Goal
              </label>
              <input
                type="number"
                value={goalInput}
                onChange={e => setGoalInput(Number(e.target.value))}
                min={100}
                max={100000}
                step={500}
              />
            </div>

            <div className="hud-input-group">
              <label>
                <Camera size={16} />
                Photo Captures
              </label>
              <input
                type="number"
                value={photosInput}
                onChange={e => setPhotosInput(Number(e.target.value))}
                min={1}
                max={50}
              />
            </div>

            <p className="hud-milestone-info">
              📸 Unlock a photo every <strong>{Math.floor(goalInput / photosInput)}</strong> steps
            </p>
          </div>

          <button className="hud-btn-start" onClick={handleStart}>
            <Play size={24} />
            Begin Exploration
          </button>
        </div>
      </div>
    );
  }

  // ─── ACTIVE HUD ────────────────────────────────────────────────────────
  return (
    <div className="hud-container hud-active">
      {/* Camera viewfinder */}
      <div className="hud-viewfinder">
        <video
          ref={camera.videoRef}
          autoPlay
          playsInline
          muted
          className="hud-camera-feed"
        />
        <canvas ref={camera.canvasRef} style={{ display: 'none' }} />
      </div>

      {/* Top bar */}
      <div className="hud-topbar">
        <div className="hud-photos-badge">
          <Camera size={14} />
          <span>{pagesCount}/{pedometer.totalPhotos}</span>
        </div>
        <button className="hud-sim-toggle" onClick={pedometer.toggleSimulation}>
          <Zap size={14} />
          {pedometer.isSimulating ? 'SIM ON' : 'SIM'}
        </button>
      </div>

      {/* Circular progress ring */}
      <div className="hud-ring-container">
        <svg className="hud-ring" viewBox="0 0 260 260">
          {/* Background ring */}
          <circle
            cx="130"
            cy="130"
            r="120"
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth="8"
          />
          {/* Progress ring */}
          <circle
            cx="130"
            cy="130"
            r="120"
            fill="none"
            stroke="url(#progressGradient)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 130 130)"
            className="hud-ring-progress"
          />
          {/* Milestone dots */}
          {Array.from({ length: pedometer.totalPhotos }, (_, i) => {
            const angle = ((i + 1) / pedometer.totalPhotos) * 360 - 90;
            const rad = (angle * Math.PI) / 180;
            const cx = 130 + 120 * Math.cos(rad);
            const cy = 130 + 120 * Math.sin(rad);
            const reached = pedometer.steps >= (i + 1) * pedometer.milestoneInterval;
            return (
              <circle
                key={i}
                cx={cx}
                cy={cy}
                r={reached ? 6 : 4}
                fill={reached ? '#4ade80' : 'rgba(255,255,255,0.3)'}
                className={reached ? 'hud-milestone-dot reached' : 'hud-milestone-dot'}
              />
            );
          })}
          <defs>
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#4ade80" />
              <stop offset="50%" stopColor="#22d3ee" />
              <stop offset="100%" stopColor="#a78bfa" />
            </linearGradient>
          </defs>
        </svg>

        {/* Center display */}
        <div className="hud-ring-center">
          <span className="hud-steps-count">{pedometer.steps.toLocaleString()}</span>
          <span className="hud-steps-label">/ {pedometer.goalSteps.toLocaleString()} steps</span>
        </div>
      </div>

      {/* Milestone unlock message */}
      {pedometer.canSnap && (
        <div className="hud-unlock-banner">
          <Sparkles size={16} />
          <span>Photo {pagesCount + 1} of {pedometer.totalPhotos} Ready!</span>
        </div>
      )}

      {/* Bottom controls */}
      <div className="hud-bottom-controls">
        {/* Simulation buttons */}
        {pedometer.isSimulating && (
          <div className="hud-sim-controls">
            {[100, 200, 500].map(n => (
              <button
                key={n}
                className="hud-sim-btn"
                onClick={() => pedometer.simulateSteps(n)}
              >
                <Plus size={12} />
                {n}
              </button>
            ))}
          </div>
        )}

        {/* Shutter button */}
        <button
          className={`hud-shutter ${pedometer.canSnap ? 'ready' : 'locked'} ${isUploading ? 'uploading' : ''}`}
          onClick={handleSnap}
          disabled={!pedometer.canSnap || isUploading}
        >
          {isUploading ? (
            <div className="hud-shutter-spinner" />
          ) : (
            <Camera size={32} />
          )}
        </button>

        {/* Finish button */}
        {pagesCount > 0 && (
          <button className="hud-btn-finish" onClick={handleFinish}>
            <BookOpen size={18} />
            <span>View Book</span>
          </button>
        )}
      </div>

      {/* Snap result overlay */}
      {showResult && lastSnap && (
        <div className="hud-snap-result" onClick={() => setShowResult(false)}>
          <div className="hud-snap-card">
            <h3>🎯 Meme Match!</h3>
            <p className="hud-snap-meme-name">{lastSnap.meme_name}</p>
            <p className="hud-snap-explanation">{lastSnap.explanation}</p>
            <div className="hud-snap-confidence">
              {Math.round(lastSnap.match_confidence * 100)}% match
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
