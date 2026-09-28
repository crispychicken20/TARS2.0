// src/Design/HolographicDots.js
import React, { useRef, useEffect } from "react";

const HolographicDots = ({ tarsState }) => {
  const canvasRef = useRef(null);
  const dots = useRef([]);
  const zoomRef = useRef(1);
  const mouse = useRef({ x: null, y: null });
  const globalColor = useRef("rgba(0, 191, 255, 1)"); // default blue

  // ⭐ NEW: animation intensity for thinking pulsing
  const pulseRef = useRef(0);

  // 1️⃣ MAIN CANVAS + DOT SETUP
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    let animationFrameId;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    class Dot {
      constructor() {
        this.reset();
      }

      reset() {
        this.centerX = centerX;
        this.centerY = centerY;
        this.angle = Math.random() * 2 * Math.PI;
        this.orbitRadius = Math.random() * (canvas.height * 0.4) + 80;
        this.radius = Math.random() * 2 + 0.5;
        this.baseRadius = this.radius; // ⭐ NEW: store original radius
        this.speed = 0.001 + Math.random() * 0.003;

        // Determine behavior
        const chance = Math.random();
        this.behavior = chance < 0.15 ? "shoot" : chance < 0.3 ? "revolve" : "orbit";
        this.resetShoot();

        this.originalColor = globalColor.current;
        this.currentColor = globalColor.current;
        this.colorFadeTimeout = null;
        this.updatePosition();
      }

      resetShoot() {
        if (this.behavior === "shoot") {
          this.x = Math.random() * canvas.width;
          this.y = Math.random() * canvas.height;
          const angle = Math.random() * 2 * Math.PI;
          this.vx = Math.cos(angle) * 0.5;
          this.vy = Math.sin(angle) * 0.5;
        }
      }

      updatePosition() {
        this.x =
          this.centerX +
          Math.cos(this.angle) * this.orbitRadius * zoomRef.current;
        this.y =
          this.centerY +
          Math.sin(this.angle) * this.orbitRadius * zoomRef.current;
      }

      update() {
        // ⭐ KEEPING PHYSICS EXACTLY AS IS
        if (this.behavior === "orbit") {
          this.angle += this.speed;
          this.updatePosition();
        } else if (this.behavior === "revolve") {
          this.angle -= this.speed * 1.5;
          this.orbitRadius -= 0.05;
          if (this.orbitRadius < 20) this.orbitRadius = Math.random() * 300 + 100;
          this.updatePosition();
        } else if (this.behavior === "shoot") {
          this.x += this.vx;
          this.y += this.vy;
          if (
            this.x < 0 || this.x > canvas.width ||
            this.y < 0 || this.y > canvas.height
          ) {
            this.resetShoot();
          }
        }

        // Vortex pull
        const dx = this.centerX - this.x;
        const dy = this.centerY - this.y;
        this.x += dx * 0.0008;
        this.y += dy * 0.0008;

        // Mouse hover → red
        if (mouse.current.x !== null && mouse.current.y !== null) {
          const mx = mouse.current.x - this.x;
          const my = mouse.current.y - this.y;
          const dist = Math.sqrt(mx * mx + my * my);
          if (dist < 30) {
            this.currentColor = "rgba(255, 50, 50, 1)";
            clearTimeout(this.colorFadeTimeout);
            this.colorFadeTimeout = setTimeout(() => {
              this.currentColor = this.originalColor;
            }, 500);
          }
        }

        // ⭐ NEW: apply THINKING pulsing effect
        if (tarsState === "thinking") {
          this.radius = this.baseRadius + Math.sin(pulseRef.current) * 1.3;
        } else if (tarsState === "speaking") {
          this.radius = this.baseRadius + 0.7; // slight expansion
        } else {
          this.radius = this.baseRadius;
        }
      }

      draw(ctx) {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);

        ctx.fillStyle = this.currentColor;

        // ⭐ NEW: dynamic glow
        if (tarsState === "thinking") {
          ctx.shadowBlur = 25 + Math.sin(pulseRef.current) * 15;
        } else if (tarsState === "speaking") {
          ctx.shadowBlur = 20;
        } else {
          ctx.shadowBlur = 10;
        }

        ctx.shadowColor = this.currentColor;
        ctx.fill();
      }
    }

    // Create initial dots
    dots.current = [];
    for (let i = 0; i < 350; i++) {
      dots.current.push(new Dot());
    }

    // Mouse events
    const handleMouseMove = (e) => {
      mouse.current.x = e.clientX;
      mouse.current.y = e.clientY;
    };
    const handleMouseLeave = () => {
      mouse.current.x = null;
      mouse.current.y = null;
    };

    // Zoom
    const handleWheel = (e) => {
      const delta = -e.deltaY * 0.001;
      zoomRef.current += delta;
      zoomRef.current = Math.min(Math.max(zoomRef.current, 0.4), 2.5);
    };

    const handleResize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    // MAIN ANIMATION LOOP
    const animate = () => {
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // ⭐ NEW: pulse update for THINKING mode
      if (tarsState === "thinking") {
        pulseRef.current += 0.08;
      } else {
        pulseRef.current = 0;
      }

      dots.current.forEach((dot) => {
        dot.update();
        dot.draw(ctx);
      });

      animationFrameId = requestAnimationFrame(animate);
    };

    // Event Listeners
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseleave", handleMouseLeave);
    window.addEventListener("resize", handleResize);
    window.addEventListener("wheel", handleWheel);

    animate();

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseleave", handleMouseLeave);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("wheel", handleWheel);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  // COLOR CHANGE BASED ON STATE
  useEffect(() => {
    if (tarsState === "thinking") {
      globalColor.current = "rgba(255, 120, 0, 1)"; // orange thinking
    } else if (tarsState === "speaking") {
      globalColor.current = "rgba(0, 255, 0, 1)"; // green
    } else {
      globalColor.current = "rgba(0, 191, 255, 1)"; // blue
    }

    dots.current.forEach((dot) => {
      dot.currentColor = globalColor.current;
      dot.originalColor = globalColor.current;
    });
  }, [tarsState]);

  return (
    <canvas
      ref={canvasRef}
      style={{
        display: "block",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 0,
        background: "black",
        width: "100vw",
        height: "100vh",
      }}
    />
  );
};

export default HolographicDots;
