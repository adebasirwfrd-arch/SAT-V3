import { useCallback, useRef, useState } from 'react';
import { useChartStore } from '../store/chartStore';

interface UseChartInteractionOptions {
    containerRef: React.RefObject<HTMLDivElement | null>;
    width: number;
}

/**
 * Hook for chart interactions: Pan, Zoom, Crosshair
 * Implements inertia scrolling for smooth UX
 */
export function useChartInteraction({ containerRef, width }: UseChartInteractionOptions) {
    const {
        scrollOffset,
        setScrollOffset,
        barSpacing,
        setBarSpacing,
        setCrosshair,
        data
    } = useChartStore();

    const isDragging = useRef(false);
    const lastMouseX = useRef(0);
    const velocity = useRef(0);
    const animationFrame = useRef<number>();

    // Inertia animation
    const animateInertia = useCallback(() => {
        if (Math.abs(velocity.current) < 0.1) {
            velocity.current = 0;
            return;
        }

        // Apply velocity
        const barsMoved = velocity.current / barSpacing;
        const newOffset = scrollOffset + barsMoved;

        // Clamp scroll
        const maxScroll = Math.max(0, data.length - Math.floor(width / barSpacing) + 10);
        setScrollOffset(Math.max(-10, Math.min(maxScroll, newOffset)));

        // Dampen velocity
        velocity.current *= 0.92;

        animationFrame.current = requestAnimationFrame(animateInertia);
    }, [barSpacing, scrollOffset, setScrollOffset, data.length, width]);

    const handleMouseDown = useCallback((e: React.MouseEvent) => {
        isDragging.current = true;
        lastMouseX.current = e.clientX;
        velocity.current = 0;

        if (animationFrame.current) {
            cancelAnimationFrame(animationFrame.current);
        }
    }, []);

    const handleMouseMove = useCallback((e: React.MouseEvent) => {
        // Update crosshair
        const rect = containerRef.current?.getBoundingClientRect();
        if (rect) {
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            setCrosshair({ x, y });
        }

        // Handle panning
        if (isDragging.current) {
            const dx = e.clientX - lastMouseX.current;
            velocity.current = dx;

            const barsMoved = dx / barSpacing;
            const newOffset = scrollOffset + barsMoved;

            // Clamp scroll
            const maxScroll = Math.max(0, data.length - Math.floor(width / barSpacing) + 10);
            setScrollOffset(Math.max(-10, Math.min(maxScroll, newOffset)));

            lastMouseX.current = e.clientX;
        }
    }, [containerRef, setCrosshair, barSpacing, scrollOffset, setScrollOffset, data.length, width]);

    const handleMouseUp = useCallback(() => {
        if (isDragging.current && Math.abs(velocity.current) > 2) {
            // Start inertia animation
            animationFrame.current = requestAnimationFrame(animateInertia);
        }
        isDragging.current = false;
    }, [animateInertia]);

    const handleMouseLeave = useCallback(() => {
        isDragging.current = false;
        setCrosshair(null);
    }, [setCrosshair]);

    const handleWheel = useCallback((e: React.WheelEvent) => {
        e.preventDefault();

        const zoomSensitivity = 0.1;
        const delta = Math.sign(e.deltaY) * -1;

        const newSpacing = barSpacing * (1 + delta * zoomSensitivity);
        setBarSpacing(newSpacing);
    }, [barSpacing, setBarSpacing]);

    return {
        handleMouseDown,
        handleMouseMove,
        handleMouseUp,
        handleMouseLeave,
        handleWheel,
        isDragging: isDragging.current,
    };
}
