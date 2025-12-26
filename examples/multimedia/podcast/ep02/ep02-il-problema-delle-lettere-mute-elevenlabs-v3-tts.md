# Episodio 2: Il Problema delle Lettere Mute
[storytelling tone] È il 14 gennaio 2022. [pause] Roma. [pause] Un uomo è seduto davanti a uno schermo.
[storytelling tone] Ha settantacinque documenti. [pause] Tutti in cirillico. [pause] Tutti provenienti dagli archivi del controspionaggio militare sovietico.
[documentary style] L'uomo è un analista. [pause] Non un analista di intelligence. [pause] Ma un analista e architetto software con più di venti anni di esperienza.
[documentary style] È specializzato in big data, machine learning e linguistica computazionale.
[storytelling tone] L'uomo è il nipote di Ingeborg. [pause] La donna misteriosamente scomparsa nel 1950 a Vienna.
[storytelling tone] Sa cosa sono quei documenti. [pause] Sa cosa contengono.
[dramatic pause] Ma non li può leggere. [pause] E non basta solo tradurli.
[storytelling tone] Ha un software. [pause] Si chiama newsleak. [documentary style] È stato costruito nel 2016 all'Università di Amburgo per analizzare fughe di documenti. [storytelling tone] Fa tutto da solo. [pause] Estrae nomi. [pause] Estrae luoghi. [pause] Estrae date. [pause] Li trasforma in grafi. [pause] Li rende ricercabili.
[storytelling tone] L'uomo carica i settantacinque documenti nel sistema.
[dramatic pause] Il sistema restituisce zero entità.
[documentary style] Settantacinque documenti. [pause] Zero nomi. [pause] Zero luoghi. [pause] Zero date.
[silence]
[whispers] I documenti rimangono in silenzio. [pause] Anche loro non parlano. [pause] Come tutti gli altri in questa storia.
[silence]
[storytelling tone] Dove siamo adesso? [pause] Roma, 23 febbraio 2022. [pause] Un uomo che sa costruire sistemi. [pause] E un sistema che non funziona come dovrebbe.
[dramatic pause] Teniamolo lì fermo per un momento. [pause] Perché per capire cosa non sta funzionando dobbiamo tornare indietro.
[storytelling tone] Torniamo ad Amburgo sei anni prima.
[silence]
[storytelling tone] È il 2016. [pause] Amburgo. [documentary style] L'Università riceve un finanziamento dalla Fondazione Volkswagen. [pause] Il progetto si chiama "Scienza e Giornalismo dei Dati".
[storytelling tone] Il contesto è questo. [documentary style] Nel 2010 WikiLeaks ha pubblicato il War Diary afghano. [pause] Novantaduemila documenti militari. [pause] Poi i cablogrammi diplomatici americani. [pause] Duecentocinquantamila documenti.
[dramatic pause] Nessun giornalista può leggere duecentocinquantamila documenti.
[storytelling tone] Serve software.
[storytelling tone] Il team di Amburgo costruisce una pipeline. [pause] La chiamano newsleak. [documentary style] Network of Searchable Leaks.
[documentary style] È un sistema complicato. [pause] Usa Java. [pause] Usa un framework che si chiama Apache UIMA. [pause] Fa analisi linguistica automatica.
[storytelling tone] Il cuore del sistema è la Named Entity Recognition. [pause] Riconoscimento di entità nominate. [pause] Il software legge un testo e trova automaticamente le persone. [pause] Le organizzazioni. [pause] I luoghi.
[documentary style] Il modello principale si chiama Epic. [pause] Per le lingue extra c'è Polyglot. [storytelling tone] Funzionano così. [pause] Leggono una frase. [pause] Calcolano la probabilità che ogni parola sia un nome. [pause] Considerano il contesto. [pause] Le parole intorno. [pause] La posizione nella frase. [pause] Poi classificano. [pause] Persona. [pause] Organizzazione. [pause] Luogo.
[documentary style] C'è anche Heideltime. [pause] Estrae date. [storytelling tone] "Il 14 aprile" diventa un punto nel tempo. [pause] "La settimana scorsa" diventa un intervallo calcolato.
[documentary style] C'è Elasticsearch. [pause] Un motore di ricerca. [pause] Indicizza tutto. [pause] Permette di cercare nei documenti molto velocemente.
[storytelling tone] C'è un'interfaccia web. [pause] Visualizza grafi di relazioni. [pause] Chi conosce chi. [pause] Chi menziona cosa. [pause] Quando.
[documentary style] Nel 2018 newsleak arriva alla versione 2.0. [pause] Supporta quaranta lingue. [pause] Tedesco. [pause] Inglese. [pause] Francese. [pause] Spagnolo. [pause] Arabo. [pause] Cinese.
[storytelling tone] Ci sono demo pubbliche online. [documentary style] Il corpus Enron. [pause] Centoventicinquemila email aziendali americane. [pause] Il caso NSU. [pause] Dodicimila documenti parlamentari tedeschi su un gruppo neonazista. [pause] La seconda guerra mondiale. [pause] Ventisettemila articoli Wikipedia in più lingue.
[storytelling tone] Il sistema funziona.
[dramatic pause] Poi arriva il 2020.
[silence]
[storytelling tone] Nel 2020 il progetto si ferma. [pause] L'ultimo commit sul repository è di mesi prima. [pause] Il team si è disperso. [pause] L'Università ha altre priorità.
[storytelling tone] newsleak diventa un software fantasma. [pause] Esiste. [pause] È pubblico. [pause] Chiunque può scaricarlo. [whispers] Ma nessuno lo mantiene.
[documentary style] Cinquantotto stelle su GitHub. [pause] Diciassette fork. [dramatic pause] Zero attività.
[silence]


[storytelling tone] Ma torniamo a Roma. [pause] Torniamo a quel febbraio del 2022.
[storytelling tone] L'uomo davanti allo schermo conosce newsleak. [pause] Lo ha trovato cercando strumenti per analizzare grandi quantità di documenti. [pause] Lo ha installato. [pause] Lo ha fatto funzionare.
[storytelling tone] E adesso ha settantacinque documenti che il software non riesce a leggere.
[storytelling tone] Ma da dove vengono questi documenti? [pause] E perché sono in cirillico?
[storytelling tone] Per capirlo dobbiamo fare un salto. [pause] Indietro nel tempo e tornare a Vienna.
[silence]
[storytelling tone] È il 12 agosto 1950. [pause] Una donna cammina verso la stazione Est. [pause] Ha ventitré anni.
[documentary style] Si chiama Ingeborg Loucek. [pause] Alias Ingeborg Novak. [pause] Alias Ingeborg Bucek.
[dramatic pause] Forse.
[storytelling tone] Sta andando a trovare suo figlio a Wels. [dramatic pause] Non ci arriva. [pause] La arrestano prima.
[documentary style] Il 21 ottobre dello stesso anno un tribunale militare a Baden la condanna a morte. [pause] L'accusa è spionaggio a favore degli Stati Uniti d'America.
[storytelling tone] Per decenni la sua storia resta sepolta. [pause] Nessuno sa cosa le sia successo. [pause] La famiglia non sa. [pause] Gli storici non sanno.
[storytelling tone] Suo figlio di tre anni. [pause] Hans Peter viene "prelevato" dai servizi segreti austriaci due giorni dopo. [documentary style] Esce dal programma di protezione solo nel 1965.
[storytelling tone] La madre di Ingeborg [pause] la nonna dell'analista. [pause] Muore nel 1992 senza sapere la verità.
[dramatic pause][whispers] Per tutta la vita alle domande ha risposto: "Non dovete parlare. Ci ammazzano tutti."
[silence]
[storytelling tone] Poi nel 2009 il Cremlino declassifica gli archivi dell'NKVD e dello SMERSH. [documentary style] Il controspionaggio militare sovietico.
[storytelling tone] Tra quei documenti c'è il fascicolo di Ingeborg Loucek.
[documentary style] Un team di ricercatori austriaci dell'Istituto Ludwig Boltzmann di Graz ottiene accesso agli archivi. [pause] Li analizza. [pause] Nel 2009 pubblica un libro. [pause] Si chiama "Stalins letzte Opfer". [pause] Le ultime vittime di Stalin.
[storytelling tone] Il libro racconta la storia di Ingeborg. [pause] L'arresto. [pause] Il processo. [pause] La condanna. [pause] L'esecuzione.
[storytelling tone] Ma racconta anche altro. [pause] Racconta incongruenze. [pause] Date che non tornano. [pause] Dettagli oscuri. [pause] Versioni contraddittorie.
[storytelling tone] L'uomo a Roma vuole capire queste incongruenze.
[storytelling tone] Ha i documenti declassificati. [pause] Sono pubblici dal 2009. [pause] Chiunque può accedervi. [pause] Ma sono in russo. [pause] E non sono tutti.
[storytelling tone] L'uomo parla italiano. [pause] Parla inglese. [pause] Parla tedesco.
[dramatic pause] Ma non conosce il russo.
[silence]
[storytelling tone] Torniamo a Roma. [pause] Torniamo a quel problema tecnico.
[storytelling tone] L'uomo carica i documenti su newsleak. [pause] Il sistema fallisce. [dramatic pause] Zero entità estratte.
[storytelling tone] Perché?
[storytelling tone] Il problema è l'alfabeto.
[documentary style] Il Named Entity Recognition di newsleak usa un modello che si chiama Polyglot. [pause] È stato addestrato su quaranta lingue. [storytelling tone] Ma Polyglot ha un problema. [dramatic pause] Non riconosce bene il cirillico.
[storytelling tone] Vede caratteri. [pause] Non vede strutture. [pause] Vede forme. [pause] Non vede parole.
[dramatic pause] Il sistema non restituisce nulla.
[silence]
[storytelling tone] L'uomo conosce il problema. [pause] Ha lavorato sulla linguistica computazionale. [pause] Sa che esistono modelli migliori.
[documentary style] Nel 2018 Google ha pubblicato BERT. [pause] Bidirectional Encoder Representations from Transformers. [storytelling tone] Un modello linguistico che legge in entrambe le direzioni. [pause] Da sinistra a destra. [pause] Da destra a sinistra. [pause] Capisce il contesto intorno a ogni parola.
[storytelling tone] Ma BERT è un modello generale. [pause] Non è specializzato per il russo.
[storytelling tone] C'è qualcosa di meglio.
[documentary style] Si chiama DeepPavlov. [pause] È una libreria di intelligenza artificiale sviluppata dall'Istituto di Fisica e Tecnologia di Mosca. [pause] È specializzata nelle lingue slave. [pause] Russo. [pause] Ucraino. [pause] Polacco. [pause] Slovacco.
[documentary style] Il modello di Named Entity Recognition si chiama "ner ontonotes bert multi torch". [pause] È un BERT multilingue addestrato su OntoNotes. [pause] Un corpus enorme. [pause] Riconosce diciotto tipi di entità.
[dramatic pause] E funziona con il cirillico.
[silence]
[storytelling tone] L'uomo decide di fare qualcosa di complicato.
[storytelling tone] Prende newsleak. [pause] Lo smonta. [pause] Sostituisce Polyglot con DeepPavlov. [pause] Ricostruisce la pipeline. [pause] Testa.
[storytelling tone] Non è un lavoro da poco. 

[documentary style] newsleak è scritto in Java. [pause] DeepPavlov è scritto in Python. [storytelling tone] Bisogna far parlare due mondi diversi.
[storytelling tone] Costruisce un microservizio. [pause] Un piccolo server che riceve testo e restituisce entità. [pause] Lo collega alla pipeline esistente. [pause] Riaddestra il modello.
[storytelling tone] Ci vogliono alcuni mesi. [pause] Anche perché nel frattempo è scoppiata la guerra in Ucraina. [pause] E lui se ne sta occupando per conto del governo italiano.
[documentary style] Nel 2023 il sistema funziona.
[storytelling tone] L'uomo carica di nuovo i settantacinque documenti russi.
[storytelling tone] Questa volta il sistema estrae entità.
[documentary style] Kolesnikov Veniamin Semënovic. [pause] Loucek Ingeborg. [pause] Vienna. [pause] Perchtoldsdorf. [pause] Gießhübl. [pause] SMERSH. [pause] Aprile 1947. [pause] Agosto 1950.
[silence]
[whispers] I documenti iniziano a parlare.
[silence]
[storytelling tone] Parlano fin troppo, ma non abbastanza.
[silence]
[documentary style] OntoNotes riconosce diciotto tipi di entità. [pause] Persone. [pause] Organizzazioni. [pause] Luoghi. [pause] Date. [pause] Prodotti. [pause] Opere d'arte. [pause] Percentuali. [pause] Denaro.
[storytelling tone] Un'indagine di intelligence non ha bisogno di percentuali né di opere d'arte.
[storytelling tone] Ha bisogno di crittogrammi. [pause] Nomi in codice. [pause] Designazioni classificate. [pause] Unità militari. [pause] Articoli di legge.
[dramatic pause] OntoNotes non riconosce crittogrammi.
[storytelling tone] C'è un altro problema. [pause] Più profondo.
[storytelling tone] newsleak cerca per parole chiave. [pause] Tu digiti una stringa. [pause] Il sistema trova quella stringa.
[storytelling tone] Digiti "Ingeborg". [pause] Trovi tutti i documenti dove compare la parola "Ingeborg".
[storytelling tone] Ma un'indagine non funziona così.
[storytelling tone] Un analista non sa sempre quale parola cercare. [pause] A volte cerca concetti. [pause] Cerca pattern. [pause] Cerca idee.
[storytelling tone] "Mostrami documenti che parlano di fughe clandestine."
[storytelling tone] "Mostrami documenti su operazioni di esfiltrazione."
[storytelling tone] "Mostrami connessioni tra zone di occupazione e servizi segreti."
[storytelling tone] La ricerca per parole chiave non può fare questo. [dramatic pause] Non ha semantica. [pause] Cerca stringhe. [pause] Non cerca significati.
[silence]
[storytelling tone] L'uomo conosce anche questo problema. [pause] E sa che esiste una soluzione.
[documentary style] Si chiama ricerca semantica. [pause] Vector search.
[storytelling tone] Funziona così. [pause] Prendi un documento. [pause] Lo trasformi in numeri. [pause] Non numeri qualsiasi. [pause] Ma vettori. [pause] Una lista di centinaia di numeri che rappresentano il significato di un testo.
[storytelling tone] Due documenti simili per significato hanno vettori simili. [pause] Anche se usano parole e lingue diverse.
[storytelling tone] "Fuga clandestina attraverso il confine" e "esfiltrazione illegale oltre la frontiera" significano quasi la stessa cosa. [pause] In una ricerca per parole chiave sono invisibili l'uno all'altro. [pause] Nessuna parola in comune.
[storytelling tone] In una ricerca semantica sono vicini. [pause] I loro vettori puntano nella stessa direzione.
[documentary style] La tecnologia esiste. [pause] Si chiama Weaviate. [pause] È un database vettoriale. [pause] Prende testo. [pause] Lo trasforma in vettori usando modelli come quelli di OpenAI. [pause] Li indicizza. [pause] Li rende ricercabili per significato.
[storytelling tone] L'uomo integra Weaviate nel sistema. [dramatic pause] Ora può cercare concetti. [pause] Non solo stringhe.
[silence]
[storytelling tone] Ma resta il problema delle entità.
[storytelling tone] OntoNotes non riconosce crittogrammi. [pause] Non riconosce articoli di legge sovietica. [pause] Non riconosce unità militari.
[storytelling tone] Addestrare di nuovo il modello richiederebbe migliaia di esempi annotati a mano. [pause] Mesi di lavoro.
[storytelling tone] C'è un'altra strada.
[documentary style] Nel 2024 viene pubblicato un paper alla conferenza NAACL. [pause] Si chiama GLiNER. [pause] Generalist and Lightweight Named Entity Recognition.
[storytelling tone] GLiNER fa qualcosa di nuovo. [pause] Riconosce qualsiasi tipo di entità senza essere addestrato su quel tipo specifico. [documentary style] Zero-shot learning. [pause] Apprendimento a zero esempi.
[storytelling tone] Gli dai un'etichetta. [pause] "Crittogramma". [pause] Lui trova i crittogrammi. [pause] Gli dai un'etichetta. [pause] "Articolo di legge". [pause] Lui trova gli articoli di legge.
[storytelling tone] Non ha mai visto esempi di crittogrammi. [pause] Non sa cosa sia un crittogramma. [pause] Ma capisce il contesto. [pause] Capisce la struttura. [pause] Capisce dove cercare.
[documentary style] È un modello piccolo. [pause] Trecentotrenta milioni di parametri. 


[pause] Molto meno di ChatGPT. [storytelling tone] Ma sui benchmark di Named Entity Recognition batte ChatGPT.
[storytelling tone] L'uomo integra GLiNER nel sistema. [pause] Definisce sette tipi di entità per l'analisi di intelligence.
[documentary style] Persone. [pause] Organizzazioni. [pause] Luoghi. [pause] Date. [pause] Eventi. [pause] Leggi. [pause] Crittogrammi.
[storytelling tone] Testa con i documenti SMERSH.
[dramatic pause] Funziona.
[silence]
[storytelling tone] Dove siamo adesso? [pause] È il gennaio 2025. [pause] L'uomo a Roma ha un sistema che funziona.
[storytelling tone] I settantacinque documenti russi sono stati processati. [pause] Le entità estratte. [pause] I nomi. [pause] I luoghi. [pause] Le date. [pause] I crittogrammi. [pause] Tutto catalogato. [pause] Tutto ricercabile per significato.
[storytelling tone] Ma quei settantacinque documenti sono solo l'inizio.
[documentary style] Ci sono centinaia di articoli di giornale. [pause] Estratti dall'archivio nazionale austriaco tramite query SPARQL. [pause] Wiener Kurier. [pause] Salzburger Nachrichten. [pause] Die Weltpresse. [pause] Decine di testate dal 1945 al 1955.
[documentary style] Ci sono i file declassificati della CIA. [pause] I rapporti dell'OSS. [pause] I registri dei crittogrammi usati nelle operazioni clandestine.
[documentary style] Ci sono decine di schede degli Arolsen Archives. [pause] L'archivio internazionale sulla persecuzione nazista. [pause] Documenti di Auschwitz. [pause] Documenti di Buchenwald. [pause] Questionari di liberazione.
[documentary style] Ci sono una ventina di libri. [pause] Stalins letzte Opfer. [pause] SMERSH: Stalin's Secret Weapon. [pause] The Red Army in Austria. [pause] America's Secret Army. [pause] The Ratline. [pause] E molti altri. [pause] Tutti analizzati. [pause] Tutti annotati.
[documentary style] Ci sono passaporti brasiliani. [pause] Decreti di immigrazione. [pause] Permessi di soggiorno.
[storytelling tone] Migliaia di pagine. [pause] Quattro lingue. [pause] Tedesco. [pause] Russo. [pause] Portoghese. [pause] Inglese.
[storytelling tone] Tutto verificato. [pause] Tutto incrociato. [pause] Tutto ricercabile per significato.
[silence]
[storytelling tone] Può cercare "fuga da prigione militare". [pause] Trova documenti rilevanti anche se non contengono quelle parole esatte.
[storytelling tone] Può cercare "articolo 58". [pause] Trova tutti i riferimenti alla legge sovietica usata per condannare.
[storytelling tone] Può cercare "Ingeborg". [pause] Trova tutto quello che la riguarda.
[dramatic pause] E quello che trova non torna.
[silence]
[storytelling tone] I documenti dicono cose impossibili.
[storytelling tone] Date che si contraddicono. [pause] Versioni degli eventi che non combaciano.
[storytelling tone] La versione ufficiale dice una cosa. [pause] I documenti dicono un'altra.
[storytelling tone] Il libro dell'Istituto Boltzmann racconta una storia. [pause] I documenti raccontano pezzi di storie diverse.
[storytelling tone] C'è un'evasione impossibile. [pause] Un ufficiale sovietico che fugge da una prigione di massima sicurezza. [dramatic pause] L'unico a riuscirci in tutta la storia di quella prigione.
[storytelling tone] C'è una ragazza di vent'anni che procura documenti falsi attraverso contatti personali.
[storytelling tone] C'è una scomparsa improvvisa. [pause] "Partito per ignoto." [pause] Destinazione sconosciuta.
[storytelling tone] C'è un arresto nel 1950. [pause] Una condanna a morte. [pause] Un'esecuzione a Mosca.
[dramatic pause] E ci sono documenti brasiliani. [pause] Un passaporto. [pause] Una foto. [pause] Un nome diverso. [pause] Una data diversa.
[silence]
[storytelling tone] L'uomo a Roma può leggere i documenti.
[storytelling tone] Può estrarre le entità.
[storytelling tone] Il suo sistema adesso può cercare per significato.
[storytelling tone] Ma ancora non può fare una cosa. [pause] Non può ragionare. [pause] Non può confrontare versioni. [pause] Non può trovare contraddizioni automaticamente. [pause] Non può dire "questo non torna".
[storytelling tone] Per quello serve qualcos'altro.
[storytelling tone] Serve intelligenza artificiale che ragiona. [pause] Che analizza. [pause] Che confronta. [pause] Che trova anomalie.
[silence]
[matter-of-fact] Quella tecnologia esiste.
[storytelling tone] L'uomo a Roma la conosce molto bene.
[dramatic pause] Sa come integrarla nel sistema.
[silence]
*Fine Episodio 2*
