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

<h3>Text input and loading</h3>

Support for manual text input via a text field. Uploading files in .txt format. The ability to clear the input field and reset the current analysis. 

<h3>Display of the analysis results</h3> 

<h4>Graphematic level</h4>
A table with tokens and their descriptors (RE, LLE, DC, PUN, etc.). 

<h4>Morphological level</h4>
Details for each word: lemma, part of speech, grammemes (case, number, gender, tense). 

<h4>Syntactic level</h4>
Interactive dependency tree with nodes (verbs, nouns) and connections (subject, complement), school format for visualizing the result of syntactic analysis, output of information about the text. 

<h4>Semantic level</h4>
Visualization of a semantic network in the form of a table of links.

<h3>Exporting the results. </h3>

Saving data in JSON/XML formats for further software processing. CSV is a tabular representation of tokens and descriptors. SVG/PNG reports with visualization of trees. GRAPHML is a graph representation format with information about nodes.

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




