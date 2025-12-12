/* eslint-disable @typescript-eslint/no-explicit-any */

export const NetworkChartResponse: any = {
	id: "nw-ratlines-network-001",
	query:
		"Show me a network diagram with the most important persons of interest, organizations and locations",
	messages: [
		{
			type: "User",
			id: "52ce1224-0b68-4309-9d5e-8849dfdbf797",
			query_id: "c9a997e3-9104-4f3a-ad92-1c4e408104af",
			conversation_id: "e58c9b95-103b-4eb4-81a6-5c9c136e90fe",
			user_id: "6411455e37173aa73261b786be979cfa",
			payload: {
				type: "text",
				metadata: {},
				code: {
					language: "",
					title: "",
					text: "",
				},
				objects: [
					"Show me a network diagram with the most important persons of interest, organizations and locations",
				],
			},
		},
		{
			type: "user_prompt",
			id: "1216e9b6-a373-4dac-8196-ce401767f989",
			user_id: "6411455e37173aa73261b786be979cfa",
			conversation_id: "e58c9b95-103b-4eb4-81a6-5c9c136e90fe",
			query_id: "c9a997e3-9104-4f3a-ad92-1c4e408104af",
			payload: {
				prompt:
					"Show me a network diagram with the most important persons of interest, organizations and locations",
			},
		},
		{
			type: "status",
			user_id: "6411455e37173aa73261b786be979cfa",
			conversation_id: "e58c9b95-103b-4eb4-81a6-5c9c136e90fe",
			query_id: "c9a997e3-9104-4f3a-ad92-1c4e408104af",
			id: "sta-8a6ae182-a16a-4dbb-bc2e-572c71ac3abb",
			payload: {
				text: "Visualising...",
			},
		},
		{
			type: "text",
			id: "tex-495e26ec-a95d-4a0f-9c80-b3634f9c6cbf",
			user_id: "6411455e37173aa73261b786be979cfa",
			conversation_id: "e58c9b95-103b-4eb4-81a6-5c9c136e90fe",
			query_id: "c9a997e3-9104-4f3a-ad92-1c4e408104af",
			payload: {
				type: "response",
				metadata: {},
				objects: [
					{
						text: "I've created a network diagram that maps the central role of Father Draganovic and Bishop Hudal at the intersection of Vatican authority, intelligence services, and Nazi fugitive networks, with connections to primary operational locations and support organizations.",
					},
				],
			},
		},
		{
			type: "result",
			user_id: "6411455e37173aa73261b786be979cfa",
			conversation_id: "e58c9b95-103b-4eb4-81a6-5c9c136e90fe",
			query_id: "c9a997e3-9104-4f3a-ad92-1c4e408104af",
			id: "res-c396e993-1665-42f4-a61e-a544b976ba24",
			payload: {
				type: "network_chart",
				objects: [
					{
						title: "Rat Lines Network: Key Persons, Organizations & Locations",
						description:
							"Network diagram showing connections between Father Krunoslav Draganovic's rat lines organization, key Vatican and intelligence figures, major Nazi fugitives, supporting organizations, and geographic hubs. Edges represent documented relationships, co-occurrence in documents, operational connections, and geographic flow of fugitives.",
						nodes: [
							// Persons - Central Figures
							{
								id: "pope_pius_xii",
								label: "Pope Pius XII",
								type: "person",
								size: 26,
								group: "vatican_leadership",
								tooltip:
									"Head of the Catholic Church during WWII and post-war period, delegated authority to subordinates who facilitated rat lines operations",
								meta: {},
							},
							{
								id: "bishop_alois_hudal",
								label: "Bishop Alois Hudal",
								type: "person",
								size: 28,
								group: "central_figure",
								tooltip:
									"Austrian bishop and rector of Pontificio Istituto Teutonico di Santa Maria dell'Anima in Rome, key organizer of Nazi escape routes through Vatican channels",
								meta: {},
							},
							{
								id: "father_draganovic",
								label: "Father Krunoslav Draganovic",
								type: "person",
								size: 28,
								group: "central_figure",
								tooltip:
									"Croatian Catholic priest, primary architect of the rat lines, operated from Croatian National Church in Rome facilitating escape of Ustasha and Nazi war criminals",
								meta: {},
							},
							{
								id: "giovanni_montini",
								label: "Giovanni Montini (Pope Paul VI)",
								type: "person",
								size: 22,
								group: "vatican_leadership",
								tooltip:
									"Vatican official who later became Pope Paul VI, provided institutional support for escape operations through Vatican channels",
								meta: {},
							},
							{
								id: "domenico_tardini",
								label: "Domenico Tardini",
								type: "person",
								size: 18,
								group: "vatican_leadership",
								tooltip:
									"Vatican Secretary for Extraordinary Affairs, facilitated escape operations through diplomatic channels",
								meta: {},
							},
							// Persons - Nazi Fugitives
							{
								id: "adolf_eichmann",
								label: "Adolf Eichmann",
								type: "person",
								size: 22,
								group: "nazi_fugitive",
								tooltip:
									"SS-Obersturmbannfuhrer, architect of the Holocaust, escaped to Argentina via rat lines in 1950, captured by Mossad in 1960",
								meta: {},
							},
							{
								id: "josef_mengele",
								label: "Josef Mengele",
								type: "person",
								size: 22,
								group: "nazi_fugitive",
								tooltip:
									"SS physician known as 'Angel of Death' at Auschwitz, escaped to South America via rat lines, died in Brazil 1979",
								meta: {},
							},
							{
								id: "klaus_barbie",
								label: "Klaus Barbie",
								type: "person",
								size: 22,
								group: "nazi_fugitive",
								tooltip:
									"Gestapo chief of Lyon known as 'Butcher of Lyon', escaped to Bolivia via rat lines with CIC assistance, extradited to France 1983",
								meta: {},
							},
							{
								id: "ante_pavelic",
								label: "Ante Pavelic",
								type: "person",
								size: 20,
								group: "nazi_fugitive",
								tooltip:
									"Leader of Croatian Ustasha regime responsible for genocide, escaped via Vatican rat lines to Argentina",
								meta: {},
							},
							{
								id: "robert_clayton_mudd",
								label: "Robert Clayton Mudd",
								type: "person",
								size: 16,
								group: "intelligence_operative",
								tooltip:
									"CIC operative who infiltrated Draganovic's network and documented rat lines operations",
								meta: {},
							},
							// Organizations
							{
								id: "cic",
								label: "US Counter Intelligence Corps (CIC)",
								type: "organization",
								size: 24,
								group: "intelligence_service",
								tooltip:
									"US Army intelligence service that employed rat lines operatives including Hudal and Barbie for Cold War anti-communist operations",
								meta: {},
							},
							{
								id: "vatican_secretariat",
								label: "Vatican State Secretariat",
								type: "organization",
								size: 22,
								group: "vatican_institution",
								tooltip:
									"Central administrative body of the Vatican that provided institutional cover and documentation for escape operations",
								meta: {},
							},
							{
								id: "croatian_church_rome",
								label: "Croatian National Church (Rome)",
								type: "organization",
								size: 20,
								group: "vatican_institution",
								tooltip:
									"Church of San Girolamo degli Illirici in Rome, Draganovic's operational headquarters for rat lines activities",
								meta: {},
							},
							{
								id: "stille_hilfe",
								label: "Stille Hilfe (Silent Help)",
								type: "organization",
								size: 18,
								group: "support_network",
								tooltip:
									"German organization founded in 1951 to provide support for former SS members, assisted fugitives with documentation and funding",
								meta: {},
							},
							{
								id: "international_red_cross",
								label: "International Red Cross",
								type: "organization",
								size: 20,
								group: "support_network",
								tooltip:
									"Provided travel documents (titres de voyage) used by war criminals to escape, often with falsified identities",
								meta: {},
							},
							// Locations
							{
								id: "vatican_city",
								label: "Vatican City",
								type: "location",
								size: 24,
								group: "hub_location",
								tooltip:
									"Central coordination point for rat lines operations, provided safe houses, documentation, and institutional protection",
								meta: {},
							},
							{
								id: "rome_italy",
								label: "Rome, Italy",
								type: "location",
								size: 22,
								group: "hub_location",
								tooltip:
									"Primary staging area for rat lines operations, location of Croatian National Church and key Vatican institutions",
								meta: {},
							},
							{
								id: "genoa_italy",
								label: "Genoa, Italy",
								type: "location",
								size: 22,
								group: "transit_location",
								tooltip:
									"Primary embarkation port for fugitives traveling to South America, Red Cross documentation center",
								meta: {},
							},
							{
								id: "buenos_aires",
								label: "Buenos Aires, Argentina",
								type: "location",
								size: 24,
								group: "destination_location",
								tooltip:
									"Primary destination for rat lines fugitives, over 180 documented Nazi war criminals settled in Argentina",
								meta: {},
							},
							{
								id: "la_paz_bolivia",
								label: "La Paz, Bolivia",
								type: "location",
								size: 18,
								group: "destination_location",
								tooltip:
									"Secondary destination for fugitives including Klaus Barbie, who served Bolivian intelligence services",
								meta: {},
							},
						],
						edges: [
							// Vatican hierarchy and authority
							{
								from_node: "pope_pius_xii",
								to_node: "bishop_alois_hudal",
								label: "delegated authority",
								strength: 0.85,
								directed: true,
								tooltip:
									"Pope Pius XII delegated authority to Hudal who operated with tacit Vatican approval",
							},
							{
								from_node: "giovanni_montini",
								to_node: "bishop_alois_hudal",
								label: "Vatican support",
								strength: 0.8,
								directed: true,
								tooltip:
									"Montini provided Vatican institutional support for Hudal's refugee assistance activities",
							},
							{
								from_node: "giovanni_montini",
								to_node: "father_draganovic",
								label: "facilitated escape/employment",
								strength: 0.8,
								directed: true,
								tooltip:
									"Montini facilitated Draganovic's position and escape operations through Vatican channels",
							},
							{
								from_node: "domenico_tardini",
								to_node: "father_draganovic",
								label: "facilitated escape",
								strength: 0.75,
								directed: true,
								tooltip:
									"Tardini provided diplomatic cover and documentation for Draganovic's operations",
							},
							// Central collaboration
							{
								from_node: "father_draganovic",
								to_node: "bishop_alois_hudal",
								label: "primary collaboration",
								strength: 1.0,
								directed: false,
								tooltip:
									"Organized rat lines together; core leadership team coordinating escape operations",
							},
							// Fugitive facilitation
							{
								from_node: "father_draganovic",
								to_node: "ante_pavelic",
								label: "facilitated escape",
								strength: 0.9,
								directed: true,
								tooltip:
									"Draganovic personally organized Pavelic's escape from Europe to Argentina",
							},
							{
								from_node: "father_draganovic",
								to_node: "klaus_barbie",
								label: "facilitated escape",
								strength: 0.85,
								directed: true,
								tooltip:
									"Draganovic facilitated Barbie's escape to Bolivia via rat lines network",
							},
							{
								from_node: "bishop_alois_hudal",
								to_node: "adolf_eichmann",
								label: "utilized network",
								strength: 0.85,
								directed: true,
								tooltip:
									"Eichmann escaped via Hudal's network using Red Cross documentation",
							},
							{
								from_node: "bishop_alois_hudal",
								to_node: "josef_mengele",
								label: "utilized network",
								strength: 0.85,
								directed: true,
								tooltip:
									"Mengele escaped to Argentina via Hudal's Vatican rat lines network",
							},
							// Intelligence connections
							{
								from_node: "robert_clayton_mudd",
								to_node: "father_draganovic",
								label: "infiltration",
								strength: 0.8,
								directed: true,
								tooltip:
									"CIC agent Mudd infiltrated Draganovic's network to document operations",
							},
							{
								from_node: "cic",
								to_node: "bishop_alois_hudal",
								label: "employment",
								strength: 0.85,
								directed: true,
								tooltip:
									"CIC employed Hudal for anti-communist intelligence operations from 1945-1962",
							},
							// Fugitive relationships
							{
								from_node: "ante_pavelic",
								to_node: "klaus_barbie",
								label: "mutual support",
								strength: 0.7,
								directed: false,
								tooltip:
									"Ustasha and Nazi fugitives provided mutual support through shared networks",
							},
							// Organization-location relationships
							{
								from_node: "vatican_secretariat",
								to_node: "vatican_city",
								label: "headquarters",
								strength: 0.95,
								directed: true,
								tooltip:
									"Vatican State Secretariat headquartered in Vatican City",
							},
							{
								from_node: "croatian_church_rome",
								to_node: "vatican_city",
								label: "located in",
								strength: 0.9,
								directed: true,
								tooltip:
									"Croatian National Church located within Vatican jurisdiction in Rome",
							},
							// Support network connections
							{
								from_node: "stille_hilfe",
								to_node: "josef_mengele",
								label: "financial support",
								strength: 0.75,
								directed: true,
								tooltip:
									"Stille Hilfe provided ongoing financial and logistical support to Mengele in South America",
							},
							{
								from_node: "international_red_cross",
								to_node: "genoa_italy",
								label: "funded transport",
								strength: 0.85,
								directed: true,
								tooltip:
									"Red Cross provided travel documents at Genoa enabling fugitive embarkation",
							},
							// Geographic escape routes
							{
								from_node: "rome_italy",
								to_node: "genoa_italy",
								label: "escape route",
								strength: 0.9,
								directed: true,
								tooltip:
									"Primary escape corridor from Vatican safe houses to Genoa embarkation port",
							},
							{
								from_node: "genoa_italy",
								to_node: "buenos_aires",
								label: "ship transport",
								strength: 0.95,
								directed: true,
								tooltip:
									"Main maritime route for fugitive transport from Europe to South America",
							},
							{
								from_node: "buenos_aires",
								to_node: "la_paz_bolivia",
								label: "alternative route",
								strength: 0.7,
								directed: true,
								tooltip:
									"Secondary dispersal route from Argentina to Bolivia for fugitives like Barbie",
							},
							// Fugitive settlements
							{
								from_node: "klaus_barbie",
								to_node: "buenos_aires",
								label: "settled in",
								strength: 0.8,
								directed: true,
								tooltip:
									"Barbie initially settled in Buenos Aires before relocating to Bolivia",
							},
							{
								from_node: "klaus_barbie",
								to_node: "la_paz_bolivia",
								label: "fled to",
								strength: 0.85,
								directed: true,
								tooltip:
									"Barbie ultimately settled in Bolivia where he served intelligence services until 1983 extradition",
							},
						],
						layout: "force",
						_REF_ID: "visualise_network_chart_0_0",
					},
				],
				metadata: {
					chart_title:
						"Rat Lines Network: Key Persons, Organizations & Locations",
					chart_type: "network",
					total_nodes: 20,
					total_edges: 22,
				},
			},
		},
	],
};
