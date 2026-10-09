-- Finanças do Casal: um cofre por casal. "dados" é texto CIFRADO no celular;
-- daqui não dá para ler nada. "versao" sobe a cada gravação e é o que
-- detecta quando os dois gravaram ao mesmo tempo.
CREATE TABLE IF NOT EXISTS cofres (
  id         TEXT PRIMARY KEY,
  versao     INTEGER NOT NULL,
  dados      TEXT NOT NULL,
  atualizado TEXT NOT NULL
);
