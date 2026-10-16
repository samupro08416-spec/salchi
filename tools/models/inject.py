"""Mete el código y los datos de los modelos en el juego."""
import re
M = '/home/claude/models/'
p = '/tmp/claude-0/-home-claude/0074c4c1-92de-5b33-85a2-6d06eda1b94d/scratchpad/salchi-lirios.html'
s = open(p).read()
code = "\n  const FUR_LAYERS_MAX = 8;\n" + open(M + 'inflate.js').read() + open(M + 'skin.js').read() + open(M + 'builders.js').read()
a = s.index("/*MODELOS-INICIO*/") + len("/*MODELOS-INICIO*/"); b = s.index("\n  /*MODELOS-FIN*/")
s = s[:a] + code + s[b:]
a = s.index('<script type="application/json" id="salchi-models">') + len('<script type="application/json" id="salchi-models">'); b = s.index('</script>', a)
s = s[:a] + open(M + 'models.json').read() + s[b:]
open(p, 'w').write(s)
print('ok', len(s) // 1024, 'KB')
