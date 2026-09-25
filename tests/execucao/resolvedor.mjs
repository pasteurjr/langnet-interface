/**
 * Resolvedor para os testes: o webpack do app aceita import sem extensão,
 * o Node não. Este gancho acrescenta ".js" quando a resolução falha —
 * assim os testes rodam o MESMO código do app, sem alterá-lo.
 */
export async function resolve(especificador, contexto, proximo) {
  try {
    return await proximo(especificador, contexto);
  } catch (e) {
    if (especificador.startsWith('.') && !/\.[a-z]+$/i.test(especificador)) {
      for (const ext of ['.js', '.jsx', '/index.js']) {
        try { return await proximo(especificador + ext, contexto); } catch {}
      }
    }
    throw e;
  }
}
