# Episodio 2: Il Problema delle Lettere Mute

---

È il 14 gennaio 2022. Roma. Un uomo è seduto davanti a uno schermo.

Ha settantacinque documenti. Tutti in cirillico. Tutti provenienti dagli archivi del controspionaggio militare sovietico.

L'uomo è un architetto software con più di venti anni di esperienza.

Sa cosa sono questi documenti. Sa cosa contengono.

Ma non li può leggere.

Ha un software. Si chiama news leak. È stato costruito nel 2016 all'Università di Amburgo per analizzare fughe di documenti. Fa tutto da solo. Estrae nomi. Estrae luoghi. Estrae date. Li mette in grafi. Li rende ricercabili.

L'uomo carica i settantacinque documenti nel sistema.

Il sistema restituisce zero entità.

Settantacinque pagine. Zero nomi. Zero luoghi. Zero date.

---

Le lettere sono mute.

---

Dove siamo adesso? Roma, gennaio 2022. Un uomo che sa costruire sistemi. E un software che non funziona.

Teniamolo lì fermo per un momento. Perché per capire cosa non sta funzionando dobbiamo tornare indietro.

Torniamo ad Amburgo sei anni prima.

---

È il 2016. Amburgo. L'Università riceve un finanziamento dalla Fondazione Volkswagen. Il progetto si chiama "Scienza e Giornalismo dei Dati".

Il contesto è questo. Nel 2010 WikiLeaks ha pubblicato il War Diary afghano. Novantaduemila documenti militari. Poi i cablogrammi diplomatici americani. Duecentocinquantamila documenti.

Nessun giornalista può leggere duecentocinquantamila documenti.

Serve software.

Il team di Amburgo costruisce una pipeline. La chiamano news leak. Network of Searchable Leaks.

È un sistema complicato. Usa Java. Usa un framework che si chiama Apache UIMA. Fa analisi linguistica automatica.

Il cuore del sistema è il Named Entity Recognition. Riconoscimento di entità nominate. Il software legge un testo e trova automaticamente le persone. Le organizzazioni. I luoghi.

Il modello si chiama Epic. Funziona così. Legge una frase. Calcola la probabilità che ogni parola sia un nome. Considera il contesto. Le parole intorno. La posizione nella frase. Poi classifica. Persona. Organizzazione. Luogo.

C'è anche Heideltime. Estrae date. "Il 14 aprile" diventa un punto nel tempo. "La settimana scorsa" diventa un intervallo calcolato.

C'è Elasticsearch. Un motore di ricerca. Indicizza tutto. Rende cercabile.

C'è un'interfaccia web. Visualizza grafi di relazioni. Chi conosce chi. Chi menziona cosa. Quando.

Nel 2018 news leak arriva alla versione 2.0. Supporta quaranta lingue. Tedesco. Inglese. Francese. Spagnolo. Arabo. Cinese.

Ci sono demo pubbliche online. Il corpus Enron. Centoventicinquemila email aziendali americane. Il caso NSU. Dodicimila documenti parlamentari tedeschi su un gruppo neonazista. La seconda guerra mondiale. Ventisettemila articoli Wikipedia in più lingue.

Il sistema funziona.

Poi arriva il 2020.

---

Nel 2020 il progetto si ferma. L'ultimo commit sul repository è di mesi prima. Il team si è disperso. L'Università ha altre priorità.

news leak diventa un software fantasma. Esiste. È pubblico. Chiunque può scaricarlo. Ma nessuno lo mantiene.

Cinquantotto stelle su GitHub. Diciassette fork. Zero attività.

---

Ma torniamo a Roma. Torniamo a quel gennaio del 2022.

L'uomo davanti allo schermo conosce news leak. Lo ha trovato cercando strumenti per analizzare grandi quantità di documenti. Lo ha installato. Lo ha fatto funzionare.

E adesso ha settantacinque documenti che il software non riesce a leggere.

Ma da dove vengono questi documenti? E perché sono in cirillico?

Per capirlo dobbiamo fare un salto. Indietro nel tempo verso Vienna.

---

È il 12 agosto 1950. Vienna. Una donna cammina verso la stazione Est. Ha ventitré anni. Si chiama Ingeborg Loucek. Sta andando a trovare suo figlio.

Non ci arriva.

La arrestano.

Il 21 ottobre dello stesso anno un tribunale militare a Baden la condanna a morte. L'accusa è spionaggio a favore degli Stati Uniti d'America.

Per decenni la sua storia resta sepolta. Nessuno sa cosa le sia successo. La famiglia non sa. Gli storici non sanno.

La madre muore nel 1992 senza sapere la verità.

---

Poi nel 2009 il Cremlino declassifica gli archivi dello SMERSH. Morte alle Spie. Il controspionaggio militare sovietico.

Tra quei documenti c'è il fascicolo di Ingeborg Loucek.

Un team di ricercatori austriaci dell'Istituto Ludwig Boltzmann di Graz ottiene accesso agli archivi. Li analizza. Nel 2009 pubblica un libro. Si chiama "Stalins letzte Opfer". Le ultime vittime di Stalin.

Il libro racconta la storia di Ingeborg. L'arresto. Il processo. La condanna. L'esecuzione.

Ma racconta anche altro. Racconta incongruenze. Date che non tornano. Dettagli oscuri. Versioni contraddittorie.

L'uomo a Roma vuole capire queste incongruenze.

Ha scaricato i documenti declassificati. Sono pubblici dal 2009. Chiunque può accedervi. Ma sono in russo.

L'uomo parla italiano. Parla inglese. Parla tedesco.

Ma non conosce il russo.

---

Torniamo a Roma. Torniamo a quel problema tecnico.

L'uomo carica i documenti su news leak. Il sistema fallisce. Zero entità estratte.

Perché?

Il problema è l'alfabeto.

Il Named Entity Recognition di news leak usa un modello che si chiama Polyglot. È stato addestrato su quaranta lingue. Ma Polyglot ha un problema. Non riconosce bene il cirillico.

Vede caratteri. Non vede strutture. Vede forme. Non vede parole.

Il sistema non restituisce nulla.

---

L'uomo conosce il problema. Ha lavorato sulla linguistica computazionale. Sa che esistono modelli migliori.

Nel 2018 Google ha pubblicato BERT. Bidirectional Encoder Representations from Transformers. Un modello di linguaggio che legge in entrambe le direzioni. Da sinistra a destra. Da destra a sinistra. Capisce il contesto intorno a ogni parola.

Ma BERT è un modello generale. Non è specializzato per il russo.

C'è qualcosa di meglio.

Si chiama DeepPavlov. È una libreria di intelligenza artificiale sviluppata dall'Istituto di Fisica e Tecnologia di Mosca. È specializzata nelle lingue slave. Russo. Ucraino. Polacco. Slovacco.

Il modello di Named Entity Recognition si chiama "ner ontonotes bert multi torch". È un BERT multilingue addestrato su OntoNotes. Un corpus enorme. Riconosce diciotto tipi di entità. Non solo persone. Non solo organizzazioni. Non solo luoghi. Anche date. Eventi. Leggi. Prodotti. Opere d'arte.

E funziona con il cirillico.

---

L'uomo decide di fare qualcosa di complicato.

Prende news leak. Lo smonta. Sostituisce Polyglot con DeepPavlov. Ricostruisce la pipeline. Testa.

Non è un lavoro da poco. news leak è scritto in Java. DeepPavlov è scritto in Python. Bisogna far parlare due mondi diversi.

Costruisce un microservizio. Un piccolo server che riceve testo e restituisce entità. Lo collega alla pipeline esistente.

Ci vogliono alcuni mesi.

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

Un'indagine di intelligence non ha bisogno di percentuali ne di opere d'arte.

Ha bisogno di crittogrammi. Nomi in codice. Designazioni classificate. Unità militari. Articoli di legge.

OntoNotes non riconosce crittogrammi.

C'è un altro problema. Più profondo.

news leak cerca per parole chiave. Tu digiti una stringa. Il sistema trova quella stringa.

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

Funziona così. Prendi un documento. Lo trasformi in numeri. Non qualsiasi numero. Un vettore. Una lista di centinaia di numeri che rappresentano il significato del testo.

Due documenti simili per significato hanno vettori simili. Anche se usano parole e lingue diverse.

"Fuga clandestina attraverso il confine" e "esfiltrazione illegale oltre la frontiera" significano quasi la stessa cosa. In una ricerca per parole chiave sono invisibili l'uno all'altro. Nessuna parola in comune.

In una ricerca semantica sono vicini. I loro vettori puntano nella stessa direzione.

La tecnologia esiste. Si chiama Weaviate. È un database vettoriale. Prende testo. Lo trasforma in vettori usando modelli come quelli di OpenAI. Li indicizza. Li rende ricercabili per significato.

L'uomo integra Weaviate nel sistema. Ora può cercare concetti. Non solo stringhe.

---

Ma resta il problema delle entità.

OntoNotes non riconosce crittogrammi. Non riconosce articoli di legge sovietica. Non riconosce unità militari.

Addestrare un nuovo modello richiederebbe migliaia di esempi annotati a mano. Mesi di lavoro.

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

Può cercare "fuga da prigione militare". Trova documenti rilevanti anche se non contengono quelle parole esatte.

Può cercare "articolo 58". Trova tutti i riferimenti alla legge sovietica usata per condannare.

Può cercare "Ingeborg". Trova tutto quello che la riguarda.

E quello che trova non torna.

---

I documenti dicono cose impossibili.

Date che si contraddicono. Luoghi che non esistono dove dovrebbero essere. Versioni degli eventi che non combaciano.

La versione ufficiale dice una cosa. I documenti dicono un'altra.

Il libro dell'Istituto Boltzmann racconta una storia. I documenti raccontano pezzi di storie diverse.

C'è un'evasione impossibile. Un ufficiale sovietico che fugge da una prigione di massima sicurezza. L'unico a riuscirci in tutta la storia di quella prigione.

C'è una ragazza di vent'anni che procura documenti falsi attraverso contatti personali.

C'è una scomparsa improvvisa. "Partito per ignoto." Destinazione sconosciuta.

C'è un arresto nel 1950. Una condanna a morte. Un'esecuzione a Mosca.

E ci sono documenti brasiliani. Un passaporto. Una foto. Un nome diverso. Una data diversa.

---

L'uomo a Roma può leggere i documenti.

Può estrarre le entità.

Può cercare per significato.

Ma non può fare una cosa.

Non può ragionare. Non può confrontare versioni. Non può trovare contraddizioni automaticamente. Non può dire "questo non torna".

Per quello serve qualcos'altro.

Serve intelligenza artificiale che ragiona. Che analizza. Che confronta. Che trova anomalie.

---

Quella tecnologia esiste.

L'uomo a Roma la conosce molto bene.

Sa come integrarla nel sistema.

---

*Fine Episodio 2*
