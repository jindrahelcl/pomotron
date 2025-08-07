# pomotron
Vercajk na Pomovu rozlučku

## Architektura predbezne

- Raspberry Pi
  - ovládané přes klávesnici
  - napájené power bankou
  - výstup pouze repráček
  - běží na tom nějakej language model

- Language model
  - powered přes ChatGPT API
  - víc různě napromptovanejch agentů
  - puppet master rozhraní přes webovou appku na mobil kde bude vidět aktivní agent a bude se to dát přepínat

- Story interface (StoryTRON)
  - servica co běží na veřejný IP adrese
  - dostává requesty od pomovo appky
  - spravuje agenty a volá chatgpt API a responsy vrací do pomovo appky
  - dostává requesty od puppet master appky a mění aktivního agenta
  - posílá do puppet master appky nějaký basic informace o sobě a pomovo appce (online, offline, traffic)

- Puppet master appka (StoryTRON frontend)
  - ovládá aktivního agenta
  - zobrazuje historii celýho příběhu
  - ukazuje stav celýho systému
  - jde z ní posílat random kecy do pomovy appky, nebo mimikovat kecy co napsal pomo do svojí appky

- Pomova appka (PomoTRON)
  - na píčku se zapne během startupu po autologinu, měla by bejt furt na popředí, ideálně jen konzolová věc
  - úderem klávesnice zopakuje co bylo napsáno
  - speciální klávesa která zahraje help
  - speciální klávesa která vymaže vstup
  - speciální klávesa která přečte co je napsáno na vstupu
  - entr to pošle do chatbota
  - pak to počká a přečte to odpověď
  - musí to asi nějak umět handlovat když se něco posere
