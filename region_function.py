"""Curated functional-domain profile per atlas region: what a change in this
region's activity is classically associated with (motor, spatiotemporal
cognition, emotional regulation, reward/motivation, sensory, executive,
autonomic/homeostatic), and what the literature reports for *increased*
("stimulation" - electrical/DBS stimulation, an agonist, or a hyperactive
state) vs *decreased* ("inhibition" - a lesion, an antagonist, ablative DBS,
or a hypoactive state) activity there.

Two things this deliberately is NOT:
- Not a claim about the region's local excitatory/inhibitory cell identity.
  "Stimulation"/"inhibition" here means the *net regional activity* went up
  or down, from whatever cause (a drug, a lesion, a DBS setting) - not
  whether the neurons involved are glutamatergic or GABAergic.
- Not a deterministic prediction. Every entry below is the *classically
  reported* association from lesion studies, direct electrical stimulation
  mapping, or DBS trials - real brain circuits are not one-domain-one-region,
  effects are frequently bidirectional/context-dependent (e.g. subthalamic
  nucleus DBS improves motor symptoms in Parkinson's disease but can also
  increase impulsivity - Frank et al. 2007), and a real docking target's net
  effect additionally depends on whether it's an agonist or antagonist at
  that site. Treat every line as a hypothesis to weigh, not a guarantee.

Coverage: every one of this app's 28 atlas-backed regions (see
atlas_regions.ATLAS_REGIONS) has an entry - "Custom (x, y, z)" exact-
coordinate entries have no region name to look up and are skipped by
render_functional_interpretation() (interpretation.py), not given a
fabricated profile.
"""
from dataclasses import dataclass

DOMAIN_MOTOR = "Motor / motricity"
DOMAIN_SPATIOTEMPORAL = "Spatiotemporal cognition & navigation"
DOMAIN_EMOTIONAL = "Emotional regulation & mood"
DOMAIN_REWARD = "Reward & motivation"
DOMAIN_AUTONOMIC = "Autonomic & homeostatic"
DOMAIN_SENSORY = "Sensory processing"
DOMAIN_EXECUTIVE = "Executive / cognitive control"
DOMAIN_MEMORY = "Memory & learning"


@dataclass(frozen=True)
class FunctionalProfile:
    domains: tuple[str, ...]
    description: str
    stimulation_effect: str
    inhibition_effect: str
    citation: str


REGION_FUNCTION: dict[str, FunctionalProfile] = {
    "Thalamus": FunctionalProfile(
        domains=(DOMAIN_SENSORY, DOMAIN_SPATIOTEMPORAL),
        description=(
            "The brain's central sensory/motor relay and arousal hub - almost "
            "every other region's input or output passes through it, so effects "
            "here tend to propagate indirectly into many other domains."
        ),
        stimulation_effect=(
            "increased arousal/sensory throughput; therapeutic thalamic DBS "
            "(e.g. VIM) is used to suppress tremor"
        ),
        inhibition_effect="sedation, reduced sensory gating, altered consciousness",
        citation="Sherman & Guillery 2001, \"Exploring the Thalamus\"; Halassa & Kastner 2017, Nat Neurosci",
    ),
    "Striatum (Caudate)": FunctionalProfile(
        domains=(DOMAIN_EXECUTIVE, DOMAIN_MOTOR),
        description=(
            "Associative/cognitive loop of the striatum - goal-directed action "
            "selection and cognitive flexibility, alongside the motor loop below."
        ),
        stimulation_effect="facilitated action selection and habit/procedural learning",
        inhibition_effect=(
            "impaired goal-directed action selection and cognitive flexibility "
            "(dopaminergic blockade here contributes to antipsychotics' cognitive "
            "and motor side effects)"
        ),
        citation="Alexander, DeLong & Strick 1986, Annu Rev Neurosci (parallel cortico-basal ganglia loops)",
    ),
    "Striatum (Putamen)": FunctionalProfile(
        domains=(DOMAIN_MOTOR,),
        description="Sensorimotor loop of the striatum - movement initiation, scaling, and habit formation.",
        stimulation_effect="facilitated movement initiation and motor learning",
        inhibition_effect=(
            "bradykinesia and rigidity (the classic Parkinson's disease "
            "presentation follows from dopaminergic loss here)"
        ),
        citation="Alexander, DeLong & Strick 1986, Annu Rev Neurosci; Dauer & Przedborski 2003, Neuron",
    ),
    "Globus Pallidus": FunctionalProfile(
        domains=(DOMAIN_MOTOR,),
        description="Main basal ganglia output nucleus gating movement via the thalamus.",
        stimulation_effect=(
            "complex/context-dependent - high-frequency DBS here functionally "
            "suppresses pathological output and improves dyskinesia"
        ),
        inhibition_effect="reduced movement (lesioning/pallidotomy has historically been used to treat dyskinesia by reducing excess pallidal output)",
        citation="DeLong 1990, Trends Neurosci; Wichmann & DeLong 1996, Curr Opin Neurobiol",
    ),
    "Hippocampus": FunctionalProfile(
        domains=(DOMAIN_SPATIOTEMPORAL, DOMAIN_MEMORY, DOMAIN_EMOTIONAL),
        description=(
            "Spatial mapping (place cells) and episodic memory encoding "
            "(dorsal); mood/anxiety regulation (ventral)."
        ),
        stimulation_effect="explored therapeutically for memory/epilepsy modulation; mixed evidence",
        inhibition_effect=(
            "anterograde amnesia and spatial disorientation (the classic finding "
            "from bilateral hippocampal damage, patient H.M.)"
        ),
        citation="O'Keefe & Dostrovsky 1971, Brain Res (place cells); Squire 1992, Psychol Rev",
    ),
    "Amygdala": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL,),
        description="Threat/fear salience detection and emotional memory tagging.",
        stimulation_effect="heightened fear/anxiety responses (reported in direct intracranial stimulation studies)",
        inhibition_effect="blunted fear recognition and emotional reactivity",
        citation="LeDoux 2000, Annu Rev Neurosci; Adolphs et al. 1994, Nature (patient S.M.)",
    ),
    "Nucleus Accumbens": FunctionalProfile(
        domains=(DOMAIN_REWARD, DOMAIN_EMOTIONAL),
        description="Core hedonic/reward hub - reward prediction, motivation, and part of the addiction circuit.",
        stimulation_effect="increased reward-seeking and hedonic response; explored via DBS for depression/OCD/addiction",
        inhibition_effect="anhedonia-like reduction in motivation and reward responsiveness",
        citation="Schultz 1998, J Neurophysiol; Schlaepfer et al. 2008, Neuropsychopharmacology",
    ),
    "Anterior Cingulate Cortex": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL, DOMAIN_EXECUTIVE),
        description="Conflict monitoring/cognitive control (dorsal) and affective/pain-related distress processing (rostral).",
        stimulation_effect="reported affective/autonomic responses in direct stimulation mapping (including mirth/laughter at some sites)",
        inhibition_effect="reduced affective distress (historically the rationale for cingulotomy in refractory depression/OCD/chronic pain)",
        citation="Bush, Luu & Posner 2000, Trends Cogn Sci; Ballantine et al. 1987, J Neurosurg (cingulotomy)",
    ),
    "Posterior Cingulate Cortex": FunctionalProfile(
        domains=(DOMAIN_SPATIOTEMPORAL, DOMAIN_MEMORY),
        description="Default-mode network hub - self-referential thought and episodic memory retrieval/spatial orientation.",
        stimulation_effect="not well characterized in isolation; implicated in altered self-referential processing",
        inhibition_effect="disorientation and episodic memory retrieval deficits (hypometabolism here tracks early Alzheimer's disease)",
        citation="Leech & Sharp 2014, Brain",
    ),
    "Insula": FunctionalProfile(
        domains=(DOMAIN_AUTONOMIC, DOMAIN_EMOTIONAL, DOMAIN_SENSORY),
        description="Interoception (internal bodily state awareness), emotional awareness, and autonomic regulation.",
        stimulation_effect="visceral sensations (nausea, gastric awareness) and emotional responses (direct intracranial stimulation mapping)",
        inhibition_effect="impaired interoceptive awareness and blunted emotional experience",
        citation="Craig 2009, Nat Rev Neurosci; Isnard et al. 2004, Ann Neurol",
    ),
    "Primary Motor Cortex": FunctionalProfile(
        domains=(DOMAIN_MOTOR,),
        description="Direct cortical control of voluntary movement (the motor homunculus).",
        stimulation_effect="evokes involuntary contralateral movement (TMS motor-evoked potentials, direct cortical stimulation)",
        inhibition_effect="contralateral weakness/paralysis (the classic stroke/lesion presentation)",
        citation="Penfield & Boldrey 1937, Brain",
    ),
    "Somatosensory Cortex": FunctionalProfile(
        domains=(DOMAIN_SENSORY, DOMAIN_SPATIOTEMPORAL),
        description="Touch and proprioception - body-position sense that feeds spatiotemporal/motor awareness.",
        stimulation_effect="evokes paresthesia (tingling) in the corresponding body part",
        inhibition_effect="sensory loss and impaired proprioception, degrading movement precision and body-spatial awareness",
        citation="Penfield & Boldrey 1937, Brain",
    ),
    "Visual Cortex (V1)": FunctionalProfile(
        domains=(DOMAIN_SENSORY, DOMAIN_SPATIOTEMPORAL),
        description="Primary visual processing - feeds spatial awareness of the external environment.",
        stimulation_effect="evokes phosphenes (flashes of light)",
        inhibition_effect="visual field scotoma / cortical blindness in the corresponding field",
        citation="Standard neuro-ophthalmology (e.g. Horton & Hoyt 1991, Arch Ophthalmol)",
    ),
    "Auditory Cortex": FunctionalProfile(
        domains=(DOMAIN_SENSORY,),
        description="Primary auditory processing.",
        stimulation_effect="evokes auditory percepts (tones, buzzing)",
        inhibition_effect="cortical deafness or auditory agnosia (impaired sound recognition despite intact hearing)",
        citation="Standard neuro-otology; Penfield & Perot 1963, Brain",
    ),
    "Temporal Pole": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL, DOMAIN_MEMORY),
        description="Paralimbic hub integrating semantic memory with social/emotional meaning.",
        stimulation_effect="not well characterized in isolation",
        inhibition_effect="impaired semantic memory and social-emotional integration (semantic dementia involves this region)",
        citation="Olson, Plotzker & Ezzyat 2007, Brain",
    ),
    "Parietal Cortex (SPL)": FunctionalProfile(
        domains=(DOMAIN_SPATIOTEMPORAL,),
        description="Visuospatial attention and sensorimotor integration - a core spatiotemporal-awareness hub.",
        stimulation_effect="altered visuospatial attention/reach coordination",
        inhibition_effect="impaired spatial orientation and visuomotor integration (contributes to spatial neglect syndromes)",
        citation="Culham & Kanwisher 2001, Curr Opin Neurobiol; Vallar 1993, Baillieres Clin Neurol",
    ),
    "Orbitofrontal Cortex": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL, DOMAIN_EXECUTIVE, DOMAIN_REWARD),
        description="Reward valuation, decision-making, and emotional/impulse regulation.",
        stimulation_effect="not well characterized in isolation; implicated in reward-value signaling",
        inhibition_effect=(
            "disinhibition and impaired social/emotional judgment (the classic "
            "Phineas Gage presentation follows OFC damage)"
        ),
        citation="Damasio 1994, \"Descartes' Error\"; Rolls 2004, Brain Cogn",
    ),
    "Middle Frontal Gyrus": FunctionalProfile(
        domains=(DOMAIN_EXECUTIVE, DOMAIN_MEMORY),
        description="Approximates dorsolateral prefrontal territory - working memory and executive control.",
        stimulation_effect=(
            "increased regional activity is the therapeutic target of rTMS over "
            "this territory in depression treatment"
        ),
        inhibition_effect="impaired working memory and executive function (virtual-lesion rTMS studies)",
        citation="Miller & Cohen 2001, Annu Rev Neurosci; George et al. 2010, Arch Gen Psychiatry",
    ),
    "Frontal Medial Cortex": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL, DOMAIN_AUTONOMIC),
        description="Approximates ventromedial prefrontal territory - self-referential processing and emotion regulation.",
        stimulation_effect="not well characterized in isolation; implicated in emotion-regulation signaling",
        inhibition_effect="impaired emotion regulation and reduced ability to down-regulate fear/threat responses",
        citation="Ongur & Price 2000, Cereb Cortex; Etkin, Egner & Kalisch 2011, Trends Cogn Sci",
    ),
    "Frontal Pole": FunctionalProfile(
        domains=(DOMAIN_EXECUTIVE,),
        description="Highest-order executive function - metacognition and multitasking/prospective memory.",
        stimulation_effect="not well characterized in isolation",
        inhibition_effect="impaired multitasking and prospective ('remember to do X later') memory",
        citation="Ramnani & Owen 2004, Nat Rev Neurosci",
    ),
    "Precuneous Cortex": FunctionalProfile(
        domains=(DOMAIN_SPATIOTEMPORAL, DOMAIN_MEMORY),
        description="Default-mode hub for visuospatial imagery, episodic memory retrieval, and self-referential spatial awareness.",
        stimulation_effect="not well characterized in isolation",
        inhibition_effect="impaired episodic memory retrieval and visuospatial imagery",
        citation="Cavanna & Trimble 2006, Brain",
    ),
    "Angular Gyrus": FunctionalProfile(
        domains=(DOMAIN_SPATIOTEMPORAL, DOMAIN_SENSORY),
        description="Multisensory integration and spatial self-representation, at the temporo-parietal junction.",
        stimulation_effect=(
            "can evoke out-of-body-experience-like sensations and body-position "
            "illusions (direct electrical stimulation mapping)"
        ),
        inhibition_effect="impaired multisensory spatial integration and semantic processing",
        citation="Blanke et al. 2002, Nature; Seghier 2013, Neuroscientist",
    ),
    "Substantia Nigra": FunctionalProfile(
        domains=(DOMAIN_MOTOR,),
        description="Dopaminergic source (SNc) for the nigrostriatal pathway driving movement initiation.",
        stimulation_effect="facilitated movement initiation (increased dopaminergic tone)",
        inhibition_effect=(
            "bradykinesia, rigidity and tremor - loss of these neurons is the "
            "defining pathology of Parkinson's disease"
        ),
        citation="Dauer & Przedborski 2003, Neuron",
    ),
    "Ventral Tegmental Area": FunctionalProfile(
        domains=(DOMAIN_REWARD, DOMAIN_EMOTIONAL),
        description="Dopaminergic origin of the mesolimbic pathway - reward, motivation, and mood.",
        stimulation_effect="increased reward-seeking/motivated behavior (optogenetic VTA activation studies)",
        inhibition_effect="anhedonia/depressive-like phenotypes (reduced VTA activity tracks stress-induced depression models)",
        citation="Tsai et al. 2009, Science; Chaudhury et al. 2013, Nature",
    ),
    "Hypothalamus": FunctionalProfile(
        domains=(DOMAIN_AUTONOMIC,),
        description="Master homeostatic regulator - hunger, temperature, circadian rhythm, and the stress (HPA) axis.",
        stimulation_effect="activation of the corresponding homeostatic/stress response (e.g. HPA axis activation)",
        inhibition_effect="disrupted homeostatic regulation (appetite, temperature, circadian rhythm, stress response)",
        citation="Saper & Lowell 2014, Curr Biol",
    ),
    "Subthalamic Nucleus": FunctionalProfile(
        domains=(DOMAIN_MOTOR, DOMAIN_EXECUTIVE),
        description="Basal ganglia indirect-pathway node; the principal DBS target for Parkinson's disease.",
        stimulation_effect=(
            "high-frequency DBS improves Parkinsonian motor symptoms, but has "
            "also been reported to increase impulsivity in some patients"
        ),
        inhibition_effect="reduced indirect-pathway 'braking' signal - can worsen dyskinesia if over-suppressed",
        citation="Limousin et al. 1998, N Engl J Med; Frank et al. 2007, Science",
    ),
    "Habenula": FunctionalProfile(
        domains=(DOMAIN_EMOTIONAL, DOMAIN_REWARD),
        description="\"Anti-reward\" hub - suppresses midbrain dopamine signaling; lateral habenula hyperactivity is linked to depression.",
        stimulation_effect="increased negative-reward/aversive signaling; implicated in depressive symptoms when hyperactive",
        inhibition_effect="disinhibits dopaminergic reward signaling (the rationale explored for habenula-targeted depression treatment)",
        citation="Proulx, Hikosaka & Malinow 2014, Nat Neurosci",
    ),
    "Ventral Pallidum": FunctionalProfile(
        domains=(DOMAIN_REWARD,),
        description="Limbic basal ganglia output - hedonic ('liking') processing and reward-driven behavior.",
        stimulation_effect="amplified hedonic ('liking') response to rewarding stimuli",
        inhibition_effect="blunted hedonic response and reduced reward-driven motivation",
        citation="Smith, Tindell, Aldridge & Berridge 2009, Trends Neurosci",
    ),
}


def get_functional_profile(name: str) -> FunctionalProfile | None:
    return REGION_FUNCTION.get(name)
