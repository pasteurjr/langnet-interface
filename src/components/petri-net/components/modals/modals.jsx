import React, { useEffect, useRef, useState, useCallback } from "react";
import * as joint from "jointjs";


export const Modal = ({ isOpen, onClose, title, children }) => {
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
          justifyContent: "center",
          alignItems: "center",
          zIndex: 1000,
        }}
      >
        <div
          style={{
            backgroundColor: "white",
            padding: "20px",
            borderRadius: "5px",
            maxWidth: "500px",
            width: "90%",
            position: "relative",
          }}
        >
          <h2 style={{ marginBottom: "20px" }}>{title}</h2>
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
          {children}
        </div>
      </div>
    );
  };
  
  /**
   * Modal para edição de agente
   */
  export const EditAgentModal = ({ isOpen, onClose, agent, onSave }) => {
    const [formData, setFormData] = useState({});
  
    useEffect(() => {
      if (agent) {
        setFormData({ ...agent });
      }
    }, [agent]);
  
    if (!agent) return null;
  
    const handleChange = (e) => {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    };
  
    return (
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title="Editar Agente"
      >
        <div>
          <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
            <div>
              <label>Nome: </label>
              <input
                type="text"
                name="nome"
                value={formData.nome || ""}
                onChange={handleChange}
                style={{ marginLeft: "10px" }}
              />
            </div>
          </div>
          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "flex-end",
              gap: "10px",
            }}
          >
            <button onClick={onClose}>Cancelar</button>
            <button onClick={() => onSave(formData)}>Salvar</button>
          </div>
        </div>
      </Modal>
    );
  };
  
  /**
   * Modal for editing place, transition, or arc properties
   */
  
  export const EditModal = ({ isOpen, onClose, type, element, onSave }) => {
    const [formData, setFormData] = useState({});
  
    useEffect(() => {
      if (element) {
        // Verificar se o nome tem espaços no elemento original
  
        setFormData({ ...element });
      }
    }, [element]);
  
    if (!element) return null;
  
    const handleChange = (e) => {
      const value =
        e.target.type === "number"
          ? e.target.value === ""
            ? ""
            : Number(e.target.value)
          : e.target.value;
      setFormData({ ...formData, [e.target.name]: value });
    };
  
    /**
   * Modal para edição de agente
   */
  
  
    /**
     * Menu de contexto específico para agentes
     */
  
  
    // Generic field creation function
    const createField = (label, name, type, options = {}) => (
      <div>
        <label>{label}: </label>
        <input
          type={type}
          name={name}
          value={formData[name] || (type === "number" ? 0 : "")}
          onChange={handleChange}
          style={{ marginLeft: "10px" }}
          {...options}
        />
      </div>
    );
  
    const renderFields = () => {
      switch (type) {
        case "place":
          return (
            <div
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              {createField("Nome", "nome", "text")}
              {createField("Tokens", "tokens", "number", { min: "0" })}
              {createField("Delay", "delay", "number", { min: "0" })}
            </div>
          );
  
        case "transition":
          return (
            <div
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              {createField("Nome", "nome", "text")}
              {createField("Prioridade", "prioridade", "number", { min: "1" })}
              {createField("Probabilidade", "probabilidade", "number", {
                min: "0",
                max: "1",
                step: "0.1",
              })}
              {createField("Tempo", "tempo", "number", { min: "0", step: "0.1" })}
            </div>
          );
  
        case "arc":
          return (
            <div
              style={{ display: "flex", flexDirection: "column", gap: "10px" }}
            >
              {createField("Peso", "peso", "number", { min: "0" })}
            </div>
          );
  
        default:
          return null;
      }
    };
  
    return (
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={`Editar ${type === "place"
          ? "Lugar"
          : type === "transition"
            ? "Transição"
            : "Arco"
          }`}
      >
        <div>
          {renderFields()}
          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "flex-end",
              gap: "10px",
            }}
          >
            <button onClick={onClose}>Cancelar</button>
            <button onClick={() => onSave(formData)}>Salvar</button>
          </div>
        </div>
      </Modal>
    );
  };
  
  /**
   * Modal for renaming the Petri net
   */
  export const RenameModal = ({ isOpen, onClose, onSave, currentName }) => {
    const [name, setName] = useState(currentName);
  
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Nome da Rede">
        <div>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            style={{ width: "100%", padding: "5px" }}
          />
          <div
            style={{
              marginTop: "20px",
              display: "flex",
              justifyContent: "flex-end",
              gap: "10px",
            }}
          >
            <button onClick={onClose}>Cancelar</button>
            <button onClick={() => onSave(name)}>Confirmar</button>
          </div>
        </div>
      </Modal>
    );
  };
  
  /**
   * Context menu for right-click operations
   */
  /**
   * Context menu para operações de clique direito
   * Versão corrigida para lidar adequadamente com elementos de interface
   */
  export const ContextMenu = ({
    x,
    y,
    onEdit,
    onDelete,
    onExplode,
    onClose,
    element,
    type,
  }) => {
    // Determina se é uma transição de interface
    const isInterface =
      type === "transition" && element && element.isInterface === true;
  
    // Determina se é um lugar (para mostrar opção "Explodir")
    const isPlace = type === "place";
    // Determina se é um agente
    const isAgent = type === "agent";
    return (
      <div
        style={{
          position: "fixed",
          top: y,
          left: x,
          backgroundColor: "white",
          border: "1px solid #ccc",
          borderRadius: "4px",
          boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
          zIndex: 1000,
        }}
      >
        {/* A opção Editar é sempre mostrada */}
        <div
          style={{
            padding: "8px 12px",
            cursor: "pointer",
            hover: { backgroundColor: "#f5f5f5" },
          }}
          onClick={() => {
            onEdit();
            onClose();
          }}
        >
          Editar
        </div>
  
        {/* A opção Excluir é mostrada apenas se NÃO for uma interface */}
        {!isInterface && (
          <div
            style={{
              padding: "8px 12px",
              cursor: "pointer",
              borderTop: "1px solid #eee",
            }}
            onClick={() => {
              onDelete();
              onClose();
            }}
          >
            Excluir
          </div>
        )}
  
        {/* A opção Explodir é mostrada apenas para lugares */}
        {isPlace && (
          <div
            style={{
              padding: "8px 12px",
              cursor: "pointer",
              borderTop: "1px solid #eee",
            }}
            onClick={() => {
              onExplode();
              onClose();
            }}
          >
            Explodir
          </div>
        )}
      </div>
    );
  };