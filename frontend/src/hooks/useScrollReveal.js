import { useEffect, useRef, useState } from 'react';

/**
 * useScrollReveal - Hook for scroll-based reveal animations
 * 
 * Returns a ref to attach to elements and a boolean for revealed state
 * Uses IntersectionObserver for efficient scroll detection
 * 
 * @param {Object} options - Configuration options
 * @param {number} options.threshold - Visibility threshold (0-1), default 0.1
 * @param {string} options.rootMargin - Margin around root, default '-50px'
 * @param {boolean} options.triggerOnce - Only trigger once, default true
 */
export function useScrollReveal({
  threshold = 0.1,
  rootMargin = '-50px',
  triggerOnce = true,
} = {}) {
  const ref = useRef(null);
  const [isRevealed, setIsRevealed] = useState(false);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsRevealed(true);
          if (triggerOnce) {
            observer.unobserve(element);
          }
        } else if (!triggerOnce) {
          setIsRevealed(false);
        }
      },
      {
        threshold,
        rootMargin,
      }
    );

    observer.observe(element);

    return () => {
      observer.disconnect();
    };
  }, [threshold, rootMargin, triggerOnce]);

  return { ref, isRevealed };
}

/**
 * ScrollReveal Component - Wrapper for animated elements
 * 
 * @param {Object} props
 * @param {React.ReactNode} props.children - Content to animate
 * @param {string} props.animation - Animation type: 'up', 'left', 'right', 'scale'
 * @param {number} props.delay - Animation delay in ms
 * @param {string} props.className - Additional classes
 */
export function ScrollReveal({ 
  children, 
  animation = 'up', 
  delay = 0, 
  className = '',
  as: Component = 'div',
  ...props 
}) {
  const { ref, isRevealed } = useScrollReveal();

  const animationClass = {
    up: 'scroll-reveal',
    left: 'scroll-reveal-left',
    right: 'scroll-reveal-right',
    scale: 'scroll-reveal-scale',
  }[animation] || 'scroll-reveal';

  const delayClass = {
    100: 'delay-100',
    200: 'delay-200',
    300: 'delay-300',
    400: 'delay-400',
    500: 'delay-500',
  }[delay] || '';

  return (
    <Component
      ref={ref}
      className={`${animationClass} ${isRevealed ? 'revealed' : ''} ${delayClass} ${className}`}
      {...props}
    >
      {children}
    </Component>
  );
}

export default useScrollReveal;
