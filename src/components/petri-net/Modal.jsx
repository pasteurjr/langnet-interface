import React, { useState } from 'react';
const Modal = ({ isOpen, onClose, title, children }) => {
    if (!isOpen) return null;
  
    return (
      <div
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: "rgba(0, 0, 0, 0.5)",
          display: "flex",
          justifyContent: "center", // Mantém centralização do modal na tela
          alignItems: "center",     // Mantém centralização do modal na tela
          zIndex: 1000,
        }}
      >
        <div
          style={{
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "5px",
            maxWidth: "800px",      // Aumentei para ter mais espaço para o código
            width: "90%",
            position: "relative",
            textAlign: "left"       // Força alinhamento à esquerda do texto
          }}
        >
          <h2 style={{ 
            marginBottom: "20px",
            textAlign: "left"       // Força alinhamento à esquerda do título
          }}>{title}</h2>
          <button
            onClick={onClose}
            style={{
              position: "absolute",
              right: "10px",
              top: "10px",
              border: "none",
              background: "none",
              fontSize: "20px",
              cursor: "pointer",
            }}
          >
            ×
          </button>
          <div style={{ textAlign: "left" }}>  {/* Wrapper para garantir alinhamento à esquerda */}
            {children}
          </div>
        </div>
      </div>
    );
  };
export default Modal;
  