import java.lang.Integer;
import java.lang.String;
import java.lang.StringBuffer;
import java.util.Iterator;
import java.util.List;
import java.util.HashMap;
import java.util.Set;
import java.io.IOException;

import org.apache.lucene.index.IndexReader;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.CorruptIndexException;

import com.google.gson.Gson;


class J2Reader {

    private IndexReader _reader = null;

    public static int NO_DOCS = -1;
    public int numDocs = NO_DOCS;

    /* initIndex: Initializes a J2Reader instance with an index. */
    public void initIndex(String filename)
        throws CorruptIndexException, IOException
    {
        this._reader = IndexReader.open(filename);
        this.numDocs = this._reader.numDocs();
    }

    /* closeIndex: Resets reader */
    public void closeIndex() throws CorruptIndexException, IOException {
        this._reader.close();
        this.numDocs = J2Reader.NO_DOCS;
    }

    /* docAt: shorthand */
    public Document docAt(int index) throws IOException {
        return this._reader.document(index);
    }

    /* countFields: */
    public HashMap countFields(Document doc, HashMap fieldMap) {
        List fields = doc.getFields();
        int numFields = fields.size();

        if(fieldMap == null) 
            fieldMap = new HashMap();

        for(int i=0; i < numFields; i++) {
            Field f = (Field) fields.get(i);
            String mapKey = f.name();

            // Attempts to hide the quoted-header field arrangement
            if(mapKey.startsWith("quoted-header")) {
                if(mapKey.equals("quoted-header-name")) {
                    mapKey = f.stringValue();
                    if(mapKey.equals("date")) // date shows up as quoted and regular
                        continue;
                }
                else {
                    continue;
                }
            }
            
            if(!fieldMap.containsKey(mapKey)) {
                fieldMap.put(mapKey, 1);
            }
            else {
                int existingCount = (Integer) fieldMap.get(mapKey);
                fieldMap.put(mapKey, existingCount + 1);
            }
        }

        return fieldMap;
    }

    /* printAsJson: Builds a HashMap to match roughly the structure MongoDB
     *              uses and prints it as json.
     */
    public void printDocAsJson(Document doc) {
        List fields = doc.getFields();
        int numFields = fields.size();

        HashMap fieldMap = new HashMap();
        for(int i=0; i < numFields; i++) {
            Field f = (Field) fields.get(i);
            String mapKey = f.name();
            String mapVal = f.stringValue();

            // Append any existing data
            StringBuffer mapValBuffer = new StringBuffer();

            /* Catch quoted-header fields. It appears at the beginning of
             * the field list (from what I can tell) and doesn't always have
             * a confidence entry. */
            if(mapKey.startsWith("quoted-header")) {
                if(mapKey.equals("quoted-header-name")) {
                    mapKey = f.stringValue();
                    if(mapKey.equals("date")) // date shows up as quoted and regular
                       continue;
                    Field f_value = (Field) fields.get(++i);
                    mapVal = f_value.stringValue();
                }
                else {
                    continue;
                }
            }

            /* Now that we've identified our map key and buffer, we can check
             * our fieldMap for it and either store or append the value */
            if(fieldMap.containsKey(mapKey)) {
                String existingVal = (String) fieldMap.get(mapKey);
                mapValBuffer.append(existingVal + ", ");
            }

            mapValBuffer.append(mapVal);
            fieldMap.put(mapKey, mapValBuffer.toString());
        }

        Gson g = new Gson();
        System.out.println(g.toJson(fieldMap));
    }

    /* printAsJson: Renders documents between `start` and `finish` as json */
    public void printAsJson(int start, int finish) throws IOException {
        for(int i = start; i < finish; i++) {
            Document doc = this.docAt(i);
            this.printDocAsJson(doc);
        }
    }

    public void printAggFields(int start, int finish) throws IOException {
        HashMap fieldMap = new HashMap();

        // Aggregate window of docs
        for(int i = start; i < finish; i++) {
            Document doc = this.docAt(i);
            this.countFields(doc, fieldMap);
        }

        // Print out totals
        Set keys = fieldMap.keySet();
        Iterator it = keys.iterator();
        while(it.hasNext()) {
            String key = (String) it.next();
            int count = (Integer) fieldMap.get(key);
            System.out.println("Key => " + key + " || Val => " + count);
        }
    }

    /* main: allows the class to be run like a command line tool. Expects
     *       a path to a lucene index directory as the first argument.
     */
    public static void main (String[] args) throws Exception {
        if(args.length != 1) {
            System.out.println("J2Reader <dirname>");
            System.exit(1);
        }
        String indexName = args[0];
        
        J2Reader reader = new J2Reader();
        reader.initIndex(indexName);
        reader.printAsJson(0, reader.numDocs);
        //reader.printAggFields(0, reader.numDocs);
        reader.closeIndex();
    }
}
