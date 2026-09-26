// PetriPythonConverter.jsx
import React, { useState } from 'react';
import  Modal from './Modal';  // Importando o componente Modal existente

const PetriPythonConverter = ({ isOpen, onClose, petriNet }) => {
    const [pythonCode, setPythonCode] = useState('');

    const generatePythonCode = (petriNet) => {
        const code = [];
        
        // Imports
        code.push('from langnet import Lugar, Transicao, Arco, PetriNet, EstadoGlobal\n');
        
        // Header comment
        code.push('# Código gerado automaticamente para a rede ' + petriNet.nome + '\n');
        
        // Criar lugares
        code.push('# Criação dos lugares');
        petriNet.lugares.forEach(lugar => {
            const lugarStr = `lugar_${lugar.id} = Lugar(\n` +
                `    nome="${lugar.nome}",\n` +
                `    numero_tokens=${lugar.tokens},\n` +
                `    delay=${lugar.delay}\n` +
                `)\n`;
            code.push(lugarStr);
        });
        code.push('');
        
        // Criar transições
        code.push('# Criação das transições');
        petriNet.transicoes.forEach(trans => {
            // Encontrar arcos de entrada e saída para esta transição
            const arcosEntrada = petriNet.arcos
                .filter(arco => arco.destino === trans.id)
                .map(arco => `    Arco(lugar_${arco.origem}, peso=${arco.peso})`);
                
            const arcosSaida = petriNet.arcos
                .filter(arco => arco.origem === trans.id)
                .map(arco => `    Arco(lugar_${arco.destino}, peso=${arco.peso})`);
            
            const transStr = `transicao_${trans.id} = Transicao(\n` +
                `    nome="${trans.nome}",\n` +
                `    entrada=[\n${arcosEntrada.join(',\n')}\n    ],\n` +
                `    saida=[\n${arcosSaida.join(',\n')}\n    ],\n` +
                `    prioridade=${trans.prioridade},\n` +
                `    probabilidade=${trans.probabilidade},\n` +
                `    tempo=${trans.tempo}\n` +
                `)\n`;
            code.push(transStr);
        });
        code.push('');
        
        // Criar a rede
        code.push('# Criação da rede');
        code.push(`rede = PetriNet("${petriNet.nome}")\n`);
        
        // Adicionar lugares
        code.push('# Adicionar lugares à rede');
        petriNet.lugares.forEach(lugar => {
            code.push(`rede.adicionar_lugar(lugar_${lugar.id})`);
        });
        code.push('');
        
        // Adicionar transições
        code.push('# Adicionar transições à rede');
        petriNet.transicoes.forEach(trans => {
            code.push(`rede.adicionar_transicao(transicao_${trans.id})`);
        });
        code.push('');
        
        // Código para execução
        code.push('# Executar a rede');
        code.push('if __name__ == "__main__":');
        code.push('    rede.executar()');
        code.push('    print("Estado final da rede:", rede.obter_estado_rede())');
        
        return code.join('\n');
    };

    const handleConvert = () => {
        try {
            const generatedCode = generatePythonCode(petriNet);
            setPythonCode(generatedCode);
        } catch (error) {
            console.error('Erro ao converter JSON:', error);
            setPythonCode('Erro ao converter a rede para código Python');
        }
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Gerar Código Python"
        >
            <div style={{ maxHeight: "500px", overflowY: "auto", padding: "10px" }}>
                <div style={{ marginBottom: "20px" }}>
                    <h3 style={{ marginBottom: "10px", fontWeight: "bold" }}>
                        JSON da Rede de Petri
                    </h3>
                    <div style={{
                        backgroundColor: "#f5f5f5",
                        padding: "10px",
                        borderRadius: "4px"
                    }}>
                        <pre style={{ whiteSpace: "pre-wrap", fontSize: "12px" }}>
                            {JSON.stringify(petriNet, null, 2)}
                        </pre>
                    </div>
                </div>

                <button
                    onClick={handleConvert}
                    style={{
                        marginTop: "10px",
                        marginBottom: "10px",
                        padding: "5px 10px",
                        backgroundColor: "#4A90E2",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer"
                    }}
                >
                    Converter para Python
                </button>

                {pythonCode && (
                    <div style={{ marginTop: "20px" }}>
                        <h3 style={{ marginBottom: "10px", fontWeight: "bold" }}>
                            Código Python Gerado
                        </h3>
                        <div style={{
                            backgroundColor: "#f5f5f5",
                            padding: "10px",
                            borderRadius: "4px"
                        }}>
                            <pre style={{ whiteSpace: "pre-wrap", fontSize: "12px" }}>
                                {pythonCode}
                            </pre>
                        </div>
                    </div>
                )}
            </div>
        </Modal>
    );
};

export default PetriPythonConverter;