import React from "react";

export default class ErrorBoundary extends React.Component {
  constructor(props){ super(props); this.state = { hasError: false, err: null }; }
  static getDerivedStateFromError(err){ return { hasError: true, err }; }
  componentDidCatch(error, info){ console.error("ErrorBoundary:", error, info); }
  render(){
    if(this.state.hasError){
      return (
        <div style={{padding:20,fontFamily:"system-ui"}}>
          <h2>⚠️ La app encontró un error y se detuvo</h2>
          <pre style={{whiteSpace:"pre-wrap"}}>{String(this.state.err)}</pre>
          <p>Revisa también la consola del navegador (Ctrl+Shift+J).</p>
        </div>
      );
    }
    return this.props.children;
  }
}
