export const MapboxResponse: any = {
	id: "mapbox-ratlines-001",
	query: "Map the Nazi Ratline escape routes from Europe to South America",
	messages: [
		{
			type: "User",
			id: "52ce1224-0b68-4309-9d5e-8849dfdbf797",
			query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
			conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
			user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
			payload: {
				type: "text",
				metadata: {},
				code: {
					language: "",
					title: "",
					text: "",
				},
				objects: [
					"Map the Nazi rat lines escape routes from Europe to South America",
				],
			},
		},
		{
			type: "user_prompt",
			id: "f921d072-bfee-4dec-84d7-c06391567aa7",
			user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
			conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
			query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
			payload: {
				prompt:
					"Map the Nazi rat lines escape routes from Europe to South America",
			},
		},
		{
			type: "text",
			id: "tex-0933e369-0630-4786-bac6-487f11b61570",
			user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
			conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
			query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
			payload: {
				type: "response",
				metadata: {},
				objects: [
					{
						text: "I'll map the post-WWII Nazi escape routes showing the Vatican-coordinated rat lines from Europe to South America, including processing hubs, transit corridors, and destination settlements.",
					},
				],
			},
		},
		{
			type: "result",
			user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
			conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
			query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
			id: "res-7feb7362-0218-41ec-9149-eeeb5378dcd8",
			payload: {
				type: "mapbox",
				objects: [
					{
						name: "Vatican City - Rat Line Hub",
						latitude: 41.9029,
						longitude: 12.4534,
						description:
							"Sovereign state serving as institutional core of European escape network. Location where Alois Hudal and Krunoslav Draganović coordinated Nazi and Ustascha war criminal escapes. Vatican provided diplomatic immunity, ecclesiastical cover, and documentation fraud services.",
						locationType: "Operational Hub",
						id: "vatican-hub",
						weight: 10,
						_REF_ID: "location_vatican_0",
					},
					{
						name: "Rome - Croatian Nationalkirche Processing Center",
						latitude: 41.8999,
						longitude: 12.4767,
						description:
							"Croatian National Church in Rome served as fugitive processing and staging facility. Location where Krunoslav Draganović organized escape logistics. CIA intelligence report (1947) documented multiple Croatian fascist leaders residing in facility awaiting southward routing.",
						locationType: "Processing Center",
						id: "rome-croatian-church",
						weight: 9,
						_REF_ID: "location_rome_1",
					},
					{
						name: "Genoa Port - Mediterranean Embarkation Hub",
						latitude: 44.4081,
						longitude: 8.9312,
						description:
							"Primary Mediterranean port for transatlantic fugitive transport. Location where documented Nazi and Ustascha war criminals boarded commercial vessels bound for Argentina. Port operations facilitated movement of 300+ fugitives between 1945-1950s.",
						locationType: "Embarkation Port",
						id: "genoa-port",
						weight: 9,
						_REF_ID: "location_genoa_2",
					},
					{
						name: "South Tyrol - Alpine Transit Corridor",
						latitude: 46.5,
						longitude: 11.3,
						description:
							"Mountain region connecting German-speaking Europe to Italian territory. Critical smuggling corridor enabling fugitives from Austria/Germany to reach Mediterranean ports. Terrain provided natural security for clandestine movement.",
						locationType: "Transit Corridor",
						id: "south-tyrol-corridor",
						weight: 8,
						_REF_ID: "location_tyrol_3",
					},
					{
						name: "Salzburg, Austria - Intelligence Operations Base",
						latitude: 47.7999,
						longitude: 13.0453,
						description:
							"US Army Counter Intelligence Corps operational base where intelligence officers coordinated rat line operations. Secondary hub for fugitive exfiltration and Soviet defector recruitment. Proximity to Austrian-Italian border enabled efficient routing to Mediterranean ports.",
						locationType: "Intelligence Base",
						id: "salzburg-ops",
						weight: 8,
						_REF_ID: "location_salzburg_4",
					},
					{
						name: "Flensburg, Germany - Northern Collection Point",
						latitude: 54.3227,
						longitude: 10.1356,
						description:
							"Region containing Flensburg where Nazi regime's final government (Sonderbereich Mürwik) established May 1945. Rat Line Nord operated here, facilitating escape of Nazi leadership from collapsing Reich. Initial concentration point for high-level fugitives.",
						locationType: "Collection Point",
						id: "flensburg-north",
						weight: 7,
						_REF_ID: "location_flensburg_5",
					},
					{
						name: "Berlin, Germany - Origin Point",
						latitude: 52.52,
						longitude: 13.405,
						description:
							"Nazi governmental and administrative center creating demand for escape infrastructure. Nazi regime collapse (May 1945) triggered mass fugitive exodus. High concentration of war criminals and perpetrators requiring protection and smuggling.",
						locationType: "Origin Point",
						id: "berlin-origin",
						weight: 6,
						_REF_ID: "location_berlin_6",
					},
					{
						name: "Vienna, Austria - Secondary Processing Hub",
						latitude: 48.2082,
						longitude: 16.3738,
						description:
							"Austrian capital serving as secondary intelligence coordination center. US intelligence community maintained active Vienna station monitoring fugitive movements. CIC maintained active surveillance and coordination operations.",
						locationType: "Processing Hub",
						id: "vienna-hub",
						weight: 6,
						_REF_ID: "location_vienna_7",
					},
					{
						name: "Buenos Aires, Argentina - Primary South American Hub",
						latitude: -34.6037,
						longitude: -58.3816,
						description:
							"Capital and primary destination for rat line operations. Location where 180+ documented Nazi and Ustascha war criminals established post-war residences. Argentine government institutions facilitated settlement. President Perón's fascist sympathies ensured protection and integration.",
						locationType: "Settlement Hub",
						id: "buenos-aires-hub",
						weight: 10,
						_REF_ID: "location_buenosaires_8",
					},
					{
						name: "Bariloche, Argentina - Secondary Destination Hub",
						latitude: -41.1335,
						longitude: -71.3103,
						description:
							"Remote southern Argentine city serving as secondary safe-haven for Nazi war criminals. Geographic isolation and established German-speaking community enabled integration and anonymity. Lower law enforcement presence facilitated clandestine settlement.",
						locationType: "Settlement",
						id: "bariloche-settlement",
						weight: 6,
						_REF_ID: "location_bariloche_9",
					},
					{
						name: "La Paz, Bolivia - Peripheral Safe Haven",
						latitude: -16.5,
						longitude: -68.134,
						description:
							"Secondary South American destination where Klaus Barbie ('Butcher of Lyon') was smuggled. Location where Barbie lived comfortably for approximately 30 years before discovery in 1983. Demonstrates network's geographic reach beyond Argentina.",
						locationType: "Settlement",
						id: "lapaz-haven",
						weight: 5,
						_REF_ID: "location_lapaz_10",
					},
					{
						name: "Primary Escape Route: Rome to Buenos Aires",
						latitude: 41.9029,
						longitude: 12.4534,
						description:
							"Main transatlantic escape corridor from Vatican processing center through Genoa port to Buenos Aires settlement hub. Primary pathway for 180+ documented Nazi war criminal escapes (1945-1962).",
						locationType: "Escape Route",
						id: "route-rome-buenosaires",
						weight: 10,
						route: [
							[12.4534, 41.9029],
							[8.9312, 44.4081],
							[-58.3816, -34.6037],
						],
						_REF_ID: "route_primary_11",
					},
					{
						name: "Alpine Transit Route: Salzburg to Genoa",
						latitude: 47.7999,
						longitude: 13.0453,
						description:
							"Alpine corridor route from Austrian intelligence base through South Tyrol to Mediterranean embarkation port. Critical smuggling path enabling fugitives from German-speaking Europe to reach Italian ports.",
						locationType: "Transit Route",
						id: "route-alpine-transit",
						weight: 8,
						route: [
							[13.0453, 47.7999],
							[11.3, 46.5],
							[8.9312, 44.4081],
						],
						_REF_ID: "route_alpine_12",
					},
					{
						name: "Northern Route: Berlin to Salzburg",
						latitude: 52.52,
						longitude: 13.405,
						description:
							"Northern collection route from Nazi governmental center through Flensburg collection point to Austrian operations base. Initial fugitive gathering path from collapsing Reich.",
						locationType: "Collection Route",
						id: "route-northern-collection",
						weight: 6,
						route: [
							[13.405, 52.52],
							[10.1356, 54.3227],
							[13.0453, 47.7999],
						],
						_REF_ID: "route_northern_13",
					},
					{
						name: "South American Dispersal: Buenos Aires to Regional Havens",
						latitude: -34.6037,
						longitude: -58.3816,
						description:
							"Internal South American dispersal routes from primary Buenos Aires hub to secondary settlements in Bariloche (Argentina) and La Paz (Bolivia). Enabled geographic security through dispersion.",
						locationType: "Dispersal Route",
						id: "route-sa-dispersal",
						weight: 5,
						route: [
							[-58.3816, -34.6037],
							[-71.3103, -41.1335],
						],
						_REF_ID: "route_dispersal_14",
					},
					{
						name: "Bolivia Route: Buenos Aires to La Paz",
						latitude: -34.6037,
						longitude: -58.3816,
						description:
							"Secondary escape route to Bolivia. Klaus Barbie and other high-value fugitives relocated here for additional security beyond Argentine jurisdiction.",
						locationType: "Secondary Route",
						id: "route-bolivia",
						weight: 5,
						route: [
							[-58.3816, -34.6037],
							[-68.134, -16.5],
						],
						_REF_ID: "route_bolivia_15",
					},
				],
				metadata: {
					map_title: "Nazi Rat Lines: Vatican Escape Routes to South America (1945-1962)",
					total_locations: 11,
					total_routes: 5,
					route_type: "escape_network",
					operation_name: "Vatican Rat Lines / Rattenlinien",
					max_weight: 10,
					min_weight: 5,
					intelligence_context:
						"Post-WWII Nazi war criminal escape network coordinated by Vatican, CIC, and Argentine institutions. 180+ documented escapees including Eichmann, Mengele, Barbie, Rauff, Wagner, and Pavelić.",
					key_facilitators: [
						"Alois Hudal (Austrian Bishop, CIC employee 1945-1962)",
						"Krunoslav Draganović (Croatian Franciscan monk)",
					],
					temporal_scope: "1945-1962",
					documented_escapees: "180+ confirmed Nazi perpetrators",
				},
			},
		},
		{
			type: "text",
			id: "tex-6c94fd3a-ca64-4bcc-a2b3-9d0c7d8006ed",
			user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
			conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
			query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
			payload: {
				type: "response",
				metadata: {},
				objects: [
					{
						text: "Mapped the Nazi rat lines escape network showing the complete geographic infrastructure from 1945-1962. The visualization displays 11 key locations across Europe and South America: Vatican City and Rome as primary processing hubs, Genoa as Mediterranean embarkation port, South Tyrol as Alpine transit corridor, Salzburg as CIC intelligence base, and Buenos Aires/Bariloche/La Paz as South American settlement destinations. Five escape routes are mapped including the primary Rome-Genoa-Buenos Aires transatlantic corridor, the Alpine transit route from Salzburg through South Tyrol, and the South American dispersal network. Heatmap weights indicate intelligence activity intensity, with Vatican City and Buenos Aires as the highest-priority nodes in the network. The network facilitated the escape of 180+ documented Nazi war criminals including Adolf Eichmann, Josef Mengele, Klaus Barbie, Walter Rauff, Gustav Wagner, and Ante Pavelić.",
					},
				],
			},
		},
	],
};
