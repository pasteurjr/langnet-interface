/**
 * useContextState Hook - ETAPA 1 Motor Genérico
 * Hook para gerenciar Context State configurável por schema
 * Sistema genérico para qualquer projeto
 */

import { useState, useCallback, useRef } from 'react';

export const useContextState = (contextSchema = null) => {
  // Schema padrão se não for fornecido
  const defaultSchema = {
    required_fields: ['project_id', 'initialized_timestamp'],
    optional_fields: ['user_id', 'session_id'],
    field_types: {
      project_id: 'string',
      initialized_timestamp: 'datetime',
      user_id: 'string',
      session_id: 'string'
    }
  };

  const schema = contextSchema || defaultSchema;
  const contextStateRef = useRef(new Map());
  const [contextVersion, setContextVersion] = useState(0);

  // Inicializa Context State baseado no schema
  const initializeContextState = useCallback((projectConfig = null, customSchema = null) => {
    console.log('🔧 Inicializando Context State genérico');
    
    const schemaToUse = customSchema || projectConfig?.context_schema || schema;
    const newState = new Map();

    // Adiciona campos obrigatórios
    if (schemaToUse.required_fields) {
      schemaToUse.required_fields.forEach(field => {
        switch (field) {
          case 'project_id':
            newState.set(field, projectConfig?.id || 'unknown_project');
            break;
          case 'initialized_timestamp':
            newState.set(field, new Date().toISOString());
            break;
          case 'user_id':
            newState.set(field, 'default_user');
            break;
          case 'session_id':
            newState.set(field, `session_${Date.now()}`);
            break;
          default:
            newState.set(field, null);
        }
      });
    }

    // Adiciona campos opcionais com valores padrão
    if (schemaToUse.optional_fields) {
      schemaToUse.optional_fields.forEach(field => {
        if (!newState.has(field)) {
          newState.set(field, null);
        }
      });
    }

    contextStateRef.current = newState;
    setContextVersion(prev => prev + 1);

    console.log('✅ Context State inicializado:', Object.fromEntries(newState));
    return Object.fromEntries(newState);
  }, [schema]);

  // Atualiza Context State com novos dados
  const updateContextState = useCallback((updateData) => {
    if (!updateData || typeof updateData !== 'object') {
      console.warn('⚠️ updateContextState: dados inválidos', updateData);
      return;
    }

    console.log('🔄 Atualizando Context State:', updateData);

    Object.entries(updateData).forEach(([key, value]) => {
      contextStateRef.current.set(key, value);
    });

    setContextVersion(prev => prev + 1);
    
    const updated = Object.fromEntries(contextStateRef.current);
    console.log('✅ Context State atualizado:', updated);
    return updated;
  }, []);

  // Merge context state com input data de um Place
  const mergeWithContextState = useCallback((placeInputData) => {
    const contextObj = Object.fromEntries(contextStateRef.current);
    const merged = {
      ...contextObj,
      ...placeInputData
    };

    console.log('🔗 Merge Context + Place Input:', {
      context: contextObj,
      placeInput: placeInputData,
      merged: merged
    });

    return merged;
  }, []);

  // Propaga dados para próximos Places (Context State propagation)
  const propagateToNextPlaces = useCallback((outputData, nextPlaceIds = []) => {
    if (!outputData) return;

    console.log('📤 Propagando dados para próximos Places:', {
      output: outputData,
      nextPlaces: nextPlaceIds
    });

    // Atualiza context state com output do Place atual
    updateContextState(outputData);

    // Log para debug
    nextPlaceIds.forEach(placeId => {
      console.log(`📍 Dados propagados para Place ${placeId}`);
    });

    return Object.fromEntries(contextStateRef.current);
  }, [updateContextState]);

  // Converte para formato ContextStateList (formato usado pelo sistema)
  const toContextStateList = useCallback((placeId, taskName) => {
    const contextObj = Object.fromEntries(contextStateRef.current);
    
    const contextList = Object.entries(contextObj).map(([key, value]) => ({
      key: key,
      value: value,
      type: typeof value,
      source: 'context_state',
      place_id: placeId,
      task_name: taskName,
      timestamp: new Date().toISOString()
    }));

    console.log('📋 Context State List gerado:', contextList);
    return contextList;
  }, []);

  // Obtém Context State atual como objeto
  const getContextState = useCallback(() => {
    return Object.fromEntries(contextStateRef.current);
  }, []);

  // Limpa Context State
  const clearContextState = useCallback(() => {
    console.log('🗑️ Limpando Context State');
    contextStateRef.current.clear();
    setContextVersion(prev => prev + 1);
  }, []);

  // Retorna o Context State atual como objeto (reativo)
  const contextState = Object.fromEntries(contextStateRef.current);

  return {
    contextState,
    initializeContextState,
    updateContextState,
    mergeWithContextState,
    propagateToNextPlaces,
    toContextStateList,
    getContextState,
    clearContextState,
    contextVersion // Para forçar re-renders quando necessário
  };
};