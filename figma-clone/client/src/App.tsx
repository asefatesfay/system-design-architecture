import type { FC } from 'react'

const App: FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <header
        style={{
          padding: '0 16px',
          height: 48,
          display: 'flex',
          alignItems: 'center',
          borderBottom: '1px solid #e0e0e0',
          background: '#fff',
        }}
      >
        <h1 style={{ fontSize: 16, fontWeight: 600, margin: 0 }}>Figma Clone</h1>
      </header>
      <main style={{ flex: 1, background: '#f5f5f5', position: 'relative' }}>
        {/* Canvas will be mounted here in task 13 */}
        <canvas
          id="main-canvas"
          style={{ display: 'block', width: '100%', height: '100%' }}
        />
      </main>
    </div>
  )
}

export default App
