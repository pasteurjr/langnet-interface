import React from 'react';

const NotFoundPage: React.FC = () => {
  return (
    <div className="page-container">
      <h1>Página Não Encontrada</h1>
      <p>A página que você está procurando não existe ou foi movida.</p>
      <div className="placeholder-message">
        <p>Esta é uma página placeholder. A implementação completa será desenvolvida nas próximas iterações.</p>
      </div>
    </div>
  );
};

export default NotFoundPage;
