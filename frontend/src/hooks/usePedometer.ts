/**
 * usePedometer — DeviceMotion step counter with simulation toggle
 * 
 * Uses the device accelerometer to detect walking steps via peak detection
 * on the acceleration magnitude signal. Includes a simulation mode for
 * desktop testing and hackathon demos.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface PedometerState {
  steps: number;
  isTracking: boolean;
  isSimulating: boolean;
  permissionGranted: boolean;
  goalSteps: number;
  totalPhotos: number;
  milestoneInterval: number;
  currentMilestone: number;
  canSnap: boolean;
  photosLeft: number;
}

interface UsePedometerReturn extends PedometerState {
  startTracking: () => Promise<void>;
  stopTracking: () => void;
  simulateSteps: (count: number) => void;
  toggleSimulation: () => void;
  resetSteps: () => void;
  setGoal: (goal: number, photos: number) => void;
  onSnap: () => void;
}

const STEP_THRESHOLD = 1.2; // acceleration magnitude threshold for step detection
const STEP_DEBOUNCE_MS = 300; // minimum time between steps

export function usePedometer(
  initialGoal: number = 6000,
  initialPhotos: number = 10
): UsePedometerReturn {
  const [steps, setSteps] = useState(0);
  const [isTracking, setIsTracking] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [permissionGranted, setPermissionGranted] = useState(false);
  const [goalSteps, setGoalSteps] = useState(initialGoal);
  const [totalPhotos, setTotalPhotos] = useState(initialPhotos);
  const [snappedCount, setSnappedCount] = useState(0);

  const lastStepTime = useRef(0);
  const lastMagnitude = useRef(0);
  const rising = useRef(false);

  const milestoneInterval = Math.floor(goalSteps / totalPhotos);
  const currentMilestone = Math.floor(steps / milestoneInterval);
  const canSnap = currentMilestone > snappedCount && snappedCount < totalPhotos;
  const photosLeft = totalPhotos - snappedCount;

  // DeviceMotion handler — peak detection on acceleration magnitude
  const handleMotion = useCallback((event: DeviceMotionEvent) => {
    const acc = event.accelerationIncludingGravity;
    if (!acc || acc.x === null || acc.y === null || acc.z === null) return;

    const magnitude = Math.sqrt(acc.x ** 2 + acc.y ** 2 + acc.z ** 2);
    const now = Date.now();

    // Peak detection: detect when magnitude rises above threshold then falls
    if (magnitude > lastMagnitude.current) {
      rising.current = true;
    } else if (rising.current && lastMagnitude.current > STEP_THRESHOLD * 9.81) {
      if (now - lastStepTime.current > STEP_DEBOUNCE_MS) {
        lastStepTime.current = now;
        setSteps(prev => prev + 1);
      }
      rising.current = false;
    }

    lastMagnitude.current = magnitude;
  }, []);

  const startTracking = useCallback(async () => {
    // iOS 13+ requires permission
    if (typeof (DeviceMotionEvent as any).requestPermission === 'function') {
      try {
        const permission = await (DeviceMotionEvent as any).requestPermission();
        if (permission !== 'granted') {
          console.warn('[Pedometer] DeviceMotion permission denied');
          return;
        }
      } catch (e) {
        console.error('[Pedometer] Permission request failed:', e);
        return;
      }
    }

    setPermissionGranted(true);
    setIsTracking(true);
    window.addEventListener('devicemotion', handleMotion);
  }, [handleMotion]);

  const stopTracking = useCallback(() => {
    setIsTracking(false);
    window.removeEventListener('devicemotion', handleMotion);
  }, [handleMotion]);

  const simulateSteps = useCallback((count: number) => {
    setSteps(prev => Math.min(prev + count, goalSteps));
  }, [goalSteps]);

  const toggleSimulation = useCallback(() => {
    setIsSimulating(prev => !prev);
  }, []);

  const resetSteps = useCallback(() => {
    setSteps(0);
    setSnappedCount(0);
  }, []);

  const setGoal = useCallback((goal: number, photos: number) => {
    setGoalSteps(goal);
    setTotalPhotos(photos);
    setSteps(0);
    setSnappedCount(0);
  }, []);

  const onSnap = useCallback(() => {
    setSnappedCount(prev => prev + 1);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      window.removeEventListener('devicemotion', handleMotion);
    };
  }, [handleMotion]);

  return {
    steps,
    isTracking,
    isSimulating,
    permissionGranted,
    goalSteps,
    totalPhotos,
    milestoneInterval,
    currentMilestone,
    canSnap,
    photosLeft,
    startTracking,
    stopTracking,
    simulateSteps,
    toggleSimulation,
    resetSteps,
    setGoal,
    onSnap,
  };
}
