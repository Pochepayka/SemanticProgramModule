<h1>SemanticProgramModule</h1>

This software for linguistic analysis of texts and sentences in natural language is designed for multi-tiered automatic linguistic analysis of texts.

The main functions of the software being developed are linguistic analysis of natural language texts.

The system automatically analyzes text data, converting it into structured result files. The linguistic analyzer is based on such types of analyses as:
<ul>
<li>Graphematic (analysis and classification of toxins included in the natural language text)</li>
<li>Morphological (analysis and comparison of lemmas, grammatical and morphological features with the word form from the text)</li>
<li>Syntactic (analyzing and detecting relationships between tokens according to strict rules)</li>
<li>Semantic (analysis and classification of semantic relations based on the results of syntactic analysis)</li>
</ul>

The developed software module has a graphical interface in the form of a website [AnalyzeRusText](https://github.com/Pochepayka/AnalyzeRusText ).

<h2>Function</h2>

<h3>Graphematic analysis</h3>
Tokenization of text (separation into words, punctuation marks, numbers, etc.)
Normalization of text (reduction to a single case, processing of abbreviations)
Defining sentence boundaries
Identification of named entities (dates, names, organizations, etc.)

<h3>Morphological analysis</h3>
Lemmatization (reducing words to their initial form)
Definition of grammatical features (part of speech, gender, number, case, tense, etc.)
Resolution of homonymy (selection of the correct morphological interpretation)
Support for vocabulary and non-vocabulary forms

<h3>Syntactic analysis</h3>
Building a dependency tree (defining the subject, predicate, complement, etc.)
Marking up syntactic relationships (types of relationships between words)
Processing of complex sentences (compound and compound constructions)
Consideration of word order and agreement in a sentence

<h3>Semantic analysis</h3>
Identification of semantic connections between words and sentences
Exporting and visualizing results
Structured data generation (JSON, GRAPHML)
Visualization of syntax trees
Support for integration with the web interface for parsing display

<h3>Text input and loading</h3>

Support for manual text input via a text field. Uploading files in .txt format. The ability to clear the input field and reset the current analysis. 

<h3>Exporting the results</h3>

Saving data in JSON/XML formats for further software processing. CSV is a tabular representation of tokens and descriptors. SVG/PNG reports with visualization of trees. GRAPHML is a graph representation format with information about nodes.

<h2>Input and output data format</h2>

<h3>Input data</h3>
<ul>
 <li>natural language text in UTF-8 encoding</li>
 <li>the type of linguistic analysis</li>
</ul>
<h3>Output data</h3>
<ul>
 <li>the result of the analyzer in JSON format</li>
 <li>error signals</li>
</ul>

<h2>API</h2>
The software module is equipped with an API for working with it from third-party services. 

The backend is built on Flash and provides processing of requests from the frontend. When submitting the form, the data (text and selected mode) is transferred to the corresponding API endpoint, for example /api/GraphematicAnalyze for graphematic analysis. The server starts a software pipeline that processes the text with the selected analyzer and returns the result in JSON format. For example, for graphematics mode, the response includes a list of tokens with descriptors, and for semantics, nodes and connections of the semantic network.


<h2>Launch</h2>
To run the web interface on the local host in development mode, use the command:
 
### `npm start`
After open [http://localhost:3000](http://localhost:3000) to view it in your browser.


<h2>Example</h2>
<h3>Main page</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_main_page.png>

<h3>Graphematic result</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_graph_analyze.png>


<h3>Morphological result</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_morph_analyze.png>

<h3>Sintactic result (school)</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_school_sintaxis.png>

<h3>Sintactic result (tree)</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_tree_sintaxis.png>

<h3>Semantic result</h3>
<img src = https://github.com/Pochepayka/AnalyzeRusText/blob/master/src/media/png/GUI_sematic_analyze.png>




