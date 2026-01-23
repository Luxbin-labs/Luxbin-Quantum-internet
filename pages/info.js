import Head from 'next/head'
import { useEffect } from 'react'

export default function Info() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    script.async = true;
    document.head.appendChild(script);

    window.googleTranslateElementInit = () => {
      new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');
    };
  }, []);

  return (
    <>
      <Head>
        <title>Software Information & Experiments | Quantum Internet</title>
        <meta name="description" content="Detailed information on Luxbin Quantum Internet software, experiments, broadcasts, and mathematical foundations" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </Head>

      <main className="container" style={{position: 'relative', zIndex: 1, backgroundColor: 'rgba(255,255,255,0.9)', padding: '20px', borderRadius: '10px', margin: '20px', color: '#000'}}>
        <div id="google_translate_element" style={{ textAlign: 'center', marginBottom: '20px' }}></div>
        <h1 style={{fontFamily: 'Inter, sans-serif', fontSize: '3rem', fontWeight: 700, textAlign: 'center'}}>Luxbin Quantum Internet Software Information</h1>

        <section style={{margin: '20px 0'}}>
          <h2 style={{fontFamily: 'Inter, sans-serif', fontSize: '2rem'}}>Software Overview</h2>
          <p style={{fontFamily: 'Inter, sans-serif', fontSize: '1.1rem'}}>The Luxbin Quantum Internet suite is a comprehensive collection of Python scripts for simulating and interfacing with quantum networks. It includes tools for photonic broadcasting, AI agent coordination, entanglement simulations, and secure quantum communications.</p>
        </section>

        <section style={{margin: '20px 0'}}>
          <h2 style={{fontFamily: 'Inter, sans-serif', fontSize: '2rem'}}>Experiments Conducted</h2>
          <ul style={{fontFamily: 'Inter, sans-serif', fontSize: '1rem'}}>
            <li><strong>Photonic Broadcasting:</strong> Experiments with quantum_audio_broadcast.py and photonic_pixel_broadcast.py to transmit audio, video, and pixel data over photonic channels.</li>
            <li><strong>Entanglement Simulations:</strong> Using global_photonic_entanglement.py to simulate multi-continental quantum entanglement.</li>
            <li><strong>AI Agent Coordination:</strong> Deploying multi_agent_ai_quantum_network.py for secure network management across 4 countries.</li>
            <li><strong>Quantum Validation:</strong> Running quantum_validator_bridge.py for error detection and correction.</li>
            <li><strong>WiFi Quantum Integration:</strong> Testing quantum_wifi_bridge.py for wireless quantum communications.</li>
          </ul>
        </section>

        <section style={{margin: '20px 0'}}>
          <h2 style={{fontFamily: 'Inter, sans-serif', fontSize: '2rem'}}>Broadcasted Pictures and Videos</h2>
          <p style={{fontFamily: 'Inter, sans-serif', fontSize: '1.1rem'}}>The software has been used to broadcast various media over quantum-inspired channels:</p>
          <ul style={{fontFamily: 'Inter, sans-serif', fontSize: '1rem'}}>
            <li>Test audio file: <code>test_audio.wav</code> broadcasted using quantum audio scripts.</li>
            <li>Image broadcasting experiments with photonic_pixel_broadcast.py.</li>
            <li>Video simulations using quantum_video_broadcast.py.</li>
            <li>Sample image: <img src="/IMG_3537.JPG" alt="Experiment Image" style={{maxWidth: '300px', borderRadius: '5px'}} /></li>
          </ul>
        </section>

        <section style={{margin: '20px 0'}}>
          <h2 style={{fontFamily: 'Inter, sans-serif', fontSize: '2rem'}}>Linear Algebra and Fractal Geometry</h2>
          <p style={{fontFamily: 'Inter, sans-serif', fontSize: '1.1rem'}}>The software leverages advanced mathematical concepts:</p>
          <ul style={{fontFamily: 'Inter, sans-serif', fontSize: '1rem'}}>
            <li><strong>Linear Algebra:</strong> Quantum circuits are represented as matrices and vectors. Scripts use linear algebra for state evolution, entanglement calculations, and gate operations (e.g., in real_quantum_operations.py).</li>
            <li><strong>Fractal Geometry:</strong> Fractal patterns emerge in quantum simulations, such as recursive entanglement structures. The software models fractal-like quantum state spaces for complex network topologies.</li>
            <li><strong>Mathematical Foundations:</strong> Integrates concepts from quantum mechanics, including Hilbert spaces, tensor products, and Fourier transforms for signal processing.</li>
          </ul>
          <p style={{fontFamily: 'Inter, sans-serif', fontSize: '1.1rem'}}>Example: Entanglement states are described by density matrices, and fractal geometries help visualize quantum network expansions.</p>
        </section>

        <section style={{margin: '20px 0'}}>
          <h2 style={{fontFamily: 'Inter, sans-serif', fontSize: '2rem'}}>Quantum Computer Support</h2>
          <p style={{fontFamily: 'Inter, sans-serif', fontSize: '1.1rem'}}>Connects to 12+ quantum computers via luxbin_translator.py, supporting photonic (Xanadu, Quandela) and diamond NV-center systems.</p>
        </section>

        <div style={{textAlign: 'center', marginTop: '20px'}}>
          <a href="/" style={{fontFamily: 'Inter, sans-serif', color: '#007bff', textDecoration: 'none'}}>Back to Home</a>
        </div>
      </main>
    </>
  )
}