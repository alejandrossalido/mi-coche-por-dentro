import Link from 'next/link';

export default function NotFound() {
  return (
    <main style={{
      minHeight: '100vh',
      display: 'grid',
      placeItems: 'center',
      padding: '2rem',
      color: '#e8e5dc',
      background: '#08080a',
      textAlign: 'center'
    }}>
      <div>
        <strong style={{ color: '#ff5a1f', fontSize: '3rem' }}>404</strong>
        <h1 style={{ margin: '.5rem 0' }}>Esta pantalla no existe</h1>
        <p style={{ color: '#85858d', marginBottom: '1.25rem' }}>
          Vuelve al cuadro de diagnóstico para continuar trabajando con el vehículo.
        </p>
        <Link href="/" style={{ color: '#0a0a0a', background: '#c7ff35', padding: '.7rem 1rem', textDecoration: 'none', fontWeight: 800 }}>
          Volver al diagnóstico
        </Link>
      </div>
    </main>
  );
}
