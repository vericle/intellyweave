# Episodio 2: Il Problema delle Lettere Mute

---

È il 14 gennaio 2022. Roma. Un uomo è seduto davanti a uno schermo.

Ha settantacinque documenti. Tutti in cirillico. Tutti provenienti dagli archivi del controspionaggio militare sovietico.

L'uomo è un analista. Non un analista di intelligence. Ma un analista e architetto software con più di venti anni di esperienza.

È specializzato in big data, machine learning e linguistica computazionale.

L'uomo è il nipote di Ingeborg. La donna misteriosamente scomparsa nel 1950 a Vienna.

Sa cosa sono quei documenti. Sa cosa contengono.

Ma non li può leggere. E non basta solo tradurli.

Ha un software. Si chiama newsleak. È stato costruito nel 2016 all'Università di Amburgo per analizzare fughe di documenti. Fa tutto da solo. Estrae nomi. Estrae luoghi. Estrae date. Li trasforma in grafi. Li rende ricercabili.

L'uomo carica i settantacinque documenti nel sistema.

Il sistema restituisce zero entità.

Settantacinque documenti. Zero nomi. Zero luoghi. Zero date.

---

I documenti rimangono in silenzio. Anche loro non parlano. Come tutti gli altri in questa storia.

---

Roma, 23 febbraio 2022. Un uomo che sa costruire sistemi. E un sistema che non funziona come dovrebbe.

Teniamolo lì fermo per un momento. Perché per capire cosa non sta funzionando dobbiamo tornare indietro.

Torniamo ad Amburgo sei anni prima.

---

È il 2016. Amburgo. L'Università riceve un finanziamento dalla Fondazione Volkswagen. Il progetto si chiama "Scienza e Giornalismo dei Dati".

Il contesto è questo. Nel 2010 WikiLeaks ha pubblicato il War Diary afghano. Novantaduemila documenti militari. Poi i cablogrammi diplomatici americani. Duecentocinquantamila documenti.

Nessun giornalista può leggere duecentocinquantamila documenti.

Serve software.

Il team di Amburgo costruisce una pipeline. La chiamano newsleak. Network of Searchable Leaks.

È un sistema complicato. Usa Java. Usa un framework che si chiama Apache UIMA. Fa analisi linguistica automatica.

Il cuore del sistema è la Named Entity Recognition. Riconoscimento di entità nominate. Il software legge un testo e trova automaticamente le persone. Le organizzazioni. I luoghi.

Il modello principale si chiama Epic. Per le lingue extra c'è Polyglot. Funzionano così. Leggono una frase. Calcolano la probabilità che ogni parola sia un nome. Considerano il contesto. Le parole intorno. La posizione nella frase. Poi classificano. Persona. Organizzazione. Luogo.

C'è anche Heideltime. Estrae date. "Il 14 aprile" diventa un punto nel tempo. "La settimana scorsa" diventa un intervallo calcolato.

C'è Elasticsearch. Un motore di ricerca. Indicizza tutto. Permette di cercare nei documenti molto velocemente.

C'è un'interfaccia web. Visualizza grafi di relazioni. Chi conosce chi. Chi menziona cosa. Quando.

Nel 2018 newsleak arriva alla versione 2.0. Supporta quaranta lingue. Tedesco. Inglese. Francese. Spagnolo. Arabo. Cinese.

Ci sono demo pubbliche online. Il corpus Enron. Centoventicinquemila email aziendali americane. Il caso NSU. Dodicimila documenti parlamentari tedeschi su un gruppo neonazista. La seconda guerra mondiale. Ventisettemila articoli Wikipedia in più lingue.

Il sistema funziona.

Poi arriva il 2020.

---

Nel 2020 il progetto si ferma. L'ultimo commit sul repository è di mesi prima. Il team si è disperso. L'Università ha altre priorità.

newsleak diventa un software fantasma. Esiste. È pubblico. Chiunque può scaricarlo. Ma nessuno lo mantiene.

Cinquantotto stelle su GitHub. Diciassette fork. Zero attività.

---

Ma torniamo a Roma. Torniamo a quel febbraio del 2022.

L'uomo davanti allo schermo conosce newsleak. Lo ha trovato cercando strumenti per analizzare grandi quantità di documenti. Lo ha installato. Lo ha fatto funzionare.

E adesso ha settantacinque documenti che il software non riesce a leggere.

Ma da dove vengono questi documenti? E perché sono in cirillico?

Per capirlo dobbiamo fare un salto. Indietro nel tempo e tornare a Vienna.

---

È il 12 agosto 1950. Una donna cammina verso la stazione Est. Ha ventitré anni. 

Si chiama Ingeborg Loucek. Alias Ingeborg Novak. Alias Ingeborg Bucek.

Forse.

Sta andando a trovare suo figlio a Wels. Non ci arriva. La arrestano prima.

Il 21 ottobre dello stesso anno un tribunale militare a Baden la condanna a morte. L'accusa è spionaggio a favore degli Stati Uniti d'America.

Per decenni la sua storia resta sepolta. Nessuno sa cosa le sia successo. La famiglia non sa. Gli storici non sanno.

Suo figlio di tre anni. Hans Peter viene "prelevato" dai servizi segreti austriaci due giorni dopo. Esce dal programma di protezione solo nel 1965.

La madre di Ingeborg (la nonna dell'analista). Muore nel 1992 senza sapere la verità.

Per tutta la vita alle domande ha risposto: "Non dovete parlare. Ci ammazzano tutti."

---

Poi nel 2009 il Cremlino declassifica gli archivi dell'NKVD e dello SMERSH. Il controspionaggio militare sovietico.

Tra quei documenti c'è il fascicolo di Ingeborg Loucek.

Un team di ricercatori austriaci dell'Istituto Ludwig Boltzmann di Graz ottiene accesso agli archivi. Li analizza. Nel 2009 pubblica un libro. Si chiama "Stalins letzte Opfer". Le ultime vittime di Stalin.

Il libro racconta la storia di Ingeborg. L'arresto. Il processo. La condanna. L'esecuzione.

Ma racconta anche altro. Racconta incongruenze. Date che non tornano. Dettagli oscuri. Versioni contraddittorie.

L'uomo a Roma vuole capire queste incongruenze.

Ha i documenti declassificati. Sono pubblici dal 2009. Chiunque può accedervi. Ma sono in russo. E non sono tutti.

L'uomo parla italiano. Parla inglese. Parla tedesco.

Ma non conosce il russo.

---

Torniamo a Roma. Torniamo a quel problema tecnico.

L'uomo carica i documenti su newsleak. Il sistema fallisce. Zero entità estratte.

Perché?

Il problema è l'alfabeto.

Il Named Entity Recognition di newsleak usa un modello che si chiama Polyglot. È stato addestrato su quaranta lingue. Ma Polyglot ha un problema. Non riconosce bene il cirillico.

Vede caratteri. Non vede strutture. Vede forme. Non vede parole.

Il sistema non restituisce nulla.

---

L'uomo conosce il problema. Ha lavorato sulla linguistica computazionale. Sa che esistono modelli migliori.

Nel 2018 Google ha pubblicato BERT. Bidirectional Encoder Representations from Transformers. Un modello linguistico che legge in entrambe le direzioni. Da sinistra a destra. Da destra a sinistra. Capisce il contesto intorno a ogni parola.

Ma BERT è un modello generale. Non è specializzato per il russo.

C'è qualcosa di meglio.

Si chiama DeepPavlov. È una libreria di intelligenza artificiale sviluppata dall'Istituto di Fisica e Tecnologia di Mosca. È specializzata nelle lingue slave. Russo. Ucraino. Polacco. Slovacco.

Il modello di Named Entity Recognition si chiama "ner ontonotes bert multi torch". È un BERT multilingue addestrato su OntoNotes. Un corpus enorme. Riconosce diciotto tipi di entità.

E funziona con il cirillico.

---

L'uomo decide di fare qualcosa di complicato.

Prende newsleak. Lo smonta. Sostituisce Polyglot con DeepPavlov. Ricostruisce la pipeline. Testa.

Non è un lavoro da poco. newsleak è scritto in Java. DeepPavlov è scritto in Python. Bisogna far parlare due mondi diversi.

Costruisce un microservizio. Un piccolo server che riceve testo e restituisce entità. Lo collega alla pipeline esistente. Riaddestra il modello.

Ci vogliono alcuni mesi. Anche perché nel frattempo è scoppiata la guerra in Ucraina. E lui se ne sta occupando per conto del governo italiano. 

Nel 2023 il sistema funziona.

L'uomo carica di nuovo i settantacinque documenti russi.

Questa volta il sistema estrae entità.

Kolesnikov Veniamin Semënovic. Loucek Ingeborg. Vienna. Perchtoldsdorf. Gießhübl. SMERSH. Aprile 1947. Agosto 1950.

---

I documenti iniziano a parlare.

---

Parlano fin troppo, ma non abbastanza.

---

OntoNotes riconosce diciotto tipi di entità. Persone. Organizzazioni. Luoghi. Date. Prodotti. Opere d'arte. Percentuali. Denaro.

Un'indagine di intelligence non ha bisogno di percentuali né di opere d'arte.

Ha bisogno di crittogrammi. Nomi in codice. Designazioni classificate. Unità militari. Articoli di legge.

OntoNotes non riconosce crittogrammi.

C'è un altro problema. Più profondo.

newsleak cerca per parole chiave. Tu digiti una stringa. Il sistema trova quella stringa.

Digiti "Ingeborg". Trovi tutti i documenti dove compare la parola "Ingeborg".

Ma un'indagine non funziona così.

Un investigatore non sa sempre quale parola cercare. A volte cerca concetti. Cerca pattern. Cerca idee.

"Mostrami documenti che parlano di fughe clandestine."

"Mostrami documenti su operazioni di esfiltrazione."

"Mostrami connessioni tra zone di occupazione e servizi segreti."

La ricerca per parole chiave non può fare questo. Non ha semantica. Cerca stringhe. Non cerca significati.

---

L'uomo conosce anche questo problema. E sa che esiste una soluzione.

Si chiama ricerca semantica. Vector search.

Funziona così. Prendi un documento. Lo trasformi in numeri. Non numeri qualsiasi. Ma vettori. Una lista di centinaia di numeri che rappresentano il significato di un testo.

Due documenti simili per significato hanno vettori simili. Anche se usano parole e lingue diverse.

"Fuga clandestina attraverso il confine" e "esfiltrazione illegale oltre la frontiera" significano quasi la stessa cosa. In una ricerca per parole chiave sono invisibili l'uno all'altro. Nessuna parola in comune.

In una ricerca semantica sono vicini. I loro vettori puntano nella stessa direzione.

La tecnologia esiste. Si chiama Weaviate. È un database vettoriale. Prende testo. Lo trasforma in vettori usando modelli come quelli di OpenAI. Li indicizza. Li rende ricercabili per significato.

L'uomo integra Weaviate nel sistema. Ora può cercare concetti. Non solo stringhe.

---

Ma resta il problema delle entità.

OntoNotes non riconosce crittogrammi. Non riconosce articoli di legge sovietica. Non riconosce unità militari.

Addestrare di nuovo il modello richiederebbe migliaia di esempi annotati a mano. Mesi di lavoro.

C'è un'altra strada.

Nel 2024 viene pubblicato un paper alla conferenza NAACL. Si chiama GLiNER. Generalist and Lightweight Named Entity Recognition.

GLiNER fa qualcosa di nuovo. Riconosce qualsiasi tipo di entità senza essere addestrato su quel tipo specifico. Zero-shot learning. Apprendimento a zero esempi.

Gli dai un'etichetta. "Crittogramma". Lui trova i crittogrammi. Gli dai un'etichetta. "Articolo di legge". Lui trova gli articoli di legge.

Non ha mai visto esempi di crittogrammi. Non sa cosa sia un crittogramma. Ma capisce il contesto. Capisce la struttura. Capisce dove cercare.

È un modello piccolo. Trecentotrenta milioni di parametri. Molto meno di ChatGPT. Ma sui benchmark di Named Entity Recognition batte ChatGPT.

L'uomo integra GLiNER nel sistema. Definisce sette tipi di entità per l'analisi di intelligence.

Persone. Organizzazioni. Luoghi. Date. Eventi. Leggi. Crittogrammi.

Testa con i documenti SMERSH.

Funziona.

---

Dove siamo adesso? È il gennaio 2025. L'uomo a Roma ha un sistema che funziona.

I settantacinque documenti russi sono stati processati. Le entità estratte. I nomi. I luoghi. Le date. I crittogrammi. Tutto catalogato. Tutto ricercabile per significato.

Ma quei settantacinque documenti sono solo l'inizio.

Ci sono centinaia di articoli di giornale. Estratti dall'archivio nazionale austriaco tramite query SPARQL. Wiener Kurier. Salzburger Nachrichten. Die Weltpresse. Decine di testate dal 1945 al 1955.

Ci sono i file declassificati della CIA. I rapporti dell'OSS. I registri dei crittogrammi usati nelle operazioni clandestine.

Ci sono decine di schede degli Arolsen Archives. L'archivio internazionale sulla persecuzione nazista. Documenti di Auschwitz. Documenti di Buchenwald. Questionari di liberazione.

Ci sono una ventina di libri. Stalins letzte Opfer. SMERSH: Stalin's Secret Weapon. The Red Army in Austria. America's Secret Army. The Ratline. E molti altri. Tutti analizzati. Tutti annotati.

Ci sono passaporti brasiliani. Decreti di immigrazione. Permessi di soggiorno.

Migliaia di pagine. Quattro lingue. Tedesco. Russo. Portoghese. Inglese.

Tutto verificato. Tutto incrociato. Tutto ricercabile per significato.

---

Può cercare "fuga da prigione militare". Trova documenti rilevanti anche se non contengono quelle parole esatte.

Può cercare "articolo 58". Trova tutti i riferimenti alla legge sovietica usata per condannare.

Può cercare "Ingeborg". Trova tutto quello che la riguarda.

E quello che trova non torna.

---

I documenti dicono cose impossibili.

Date che si contraddicono. Versioni degli eventi che non combaciano.

La versione ufficiale dice una cosa. I documenti dicono un'altra.

Il libro dell'Istituto Boltzmann racconta una storia. I documenti raccontano pezzi di storie diverse.

C'è un'evasione impossibile. Un ufficiale sovietico che fugge da una prigione di massima sicurezza. L'unico a riuscirci in tutta la storia di quella prigione.

C'è una ragazza di vent'anni che procura documenti falsi attraverso contatti personali.

C'è una scomparsa improvvisa. "left for unknown", "Partito per ignoto." Destinazione sconosciuta.

C'è un arresto nel 1950. Una condanna a morte. Un'esecuzione a Mosca.

E ci sono documenti brasiliani. Un passaporto. Una foto. Un nome diverso. Una data diversa.

---

L'uomo a Roma può leggere i documenti.

Può estrarre le entità.

Il suo sistema adesso può cercare per significato.

Ma ancora non può fare una cosa. Non può ragionare. Non può confrontare versioni. Non può trovare contraddizioni automaticamente. Non può dire "questo non torna".

Per quello serve qualcos'altro.

Serve intelligenza artificiale che ragiona. Che analizza. Che confronta. Che trova anomalie.

---

Quella tecnologia esiste.

L'uomo a Roma la conosce molto bene.

Sa come integrarla nel sistema.

---

*Fine Episodio 2*
