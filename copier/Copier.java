import java.io.IOException;
import java.io.File;
import java.io.FileFilter;
import java.io.FileNotFoundException;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;

import java.util.Iterator;
import java.util.LinkedList;

/**
<p>Copy files from multiple destinations to a given folder and print out a report of actions.

The utility will always report failed copy events. For other actions to be reported, use the verbose mode.</p>

<p>Usage:<br/>
%COPY% -s SOURCES -d DESTINATION [-p PATTERNS] [-r] [-a] [-v] [-f|-F]</p>

<p><dl>
	<dt>-s SOURCES</dt>
	<dd>Specify the source folders to search in.</dd>
	
	<dt>-d DESTINATION</dt>
	<dd>Specify the destination folder to which all files will be copied</dd>
	
	<dt>-p PATTERNS</dt>
	<dd>Specify the filename patterns. Use "*" to specify when any chain of any length of characters may be recognized. Use "?" to specify when any single character may be recognized.
	<i>Note that on UN*X systems, It is safer to use quotation marks around each individual pattern.</i></dd>
	
	<dt>-r</dt>
	<dd>Parse folders recursively</dd>
	
	<dt>-a</dt>
	<dd>Include hidden files and folders</dd>
	
	<dt>-v</dt>
	<dd>Print detailed report of actions - namely directories created and files rejected by the patterns.</dd>
	
	<dt>-f|-F</dt>
	<dd>When a file with identical name and path is encountered in the destination folder, the default action is to ask whether or not it should be replaced. -f Specifies that files should be systematically overwritten. -F specifies that files should never be overwritten.</dd>
</dl></p>
*/
public class Copier {
	
	// modes for the command line args options
	private static final short MOD_S = 0; // for defining the source list
	private static final short MOD_D = 1; // for defining the destination folder
	private static final short MOD_P = 2; // for defining the filename patterns
	
	private static short MODE = MOD_S;
	
	// overwrite options
	private static short OWRITE = 0;
	private static final short OW_ASK = 0;
	private static final short OW_YES = 1;
	private static final short OW_NOT = 2;
	
	// other options
	private static boolean recursing = false;
	private static boolean allmode = false;
	private static boolean verbose = false;
	
	// file listing
	private static LinkedList<File> sources = new LinkedList<File>();
	private static LinkedList<String> primary = new LinkedList<String>();
	private static File destination = null;
	private static LinkedList<String> patterns = new LinkedList<String>();
	
	// stats
	private static int found = 0; // files found for copying
	private static int failed = 0; // files that failed
	
	// setting options
	private static void process(String line) {
		if(line.equals("-s") ) {MODE = MOD_S;}
		else if(line.equals("-d") ) {MODE = MOD_D;}
		else if(line.equals("-p") ) {MODE = MOD_P;}
		else if(line.equals("-r") ) {recursing = true;}
		else if(line.equals("-a") ) {allmode = true;}
		else if(line.equals("-v") ) {verbose = true;}
		else if(line.equals("-f") ) {OWRITE = OW_YES;}
		else if(line.equals("-F") ) {OWRITE = OW_NOT;}
		else {
			addItem(line);
		}
	}
	
	/** A shoddy implementation. needs breaking down for better clarity.... what to say... it works. */
	public static void main(String[] args) throws IOException {
		for(String arg : args) {process(arg);}
		
		BufferedReader conin = new BufferedReader(new InputStreamReader(System.in));
		
		// fail if the destination was not specified
		if(destination == null) {
			System.err.println("No destination specified.");
			System.exit(1);
		}
		
		// if no patterns specified, check that what we are looking for is present
		if(patterns.size() == 0) {
			System.out.println("No patterns specified. Accept all files? (y/n)");
			if( !conin.readLine().matches("y.*|Y.*") ) {System.exit(2);}
			else {setlistadd(patterns,".+");}// the "accept all" pattern
		}
		
		destination.mkdirs();// if the destination folder does not exist, make the directories that lead to it
		
		NFSIterator<File> src_iter = new NFSIterator<File>(sources);// use th custom iterator that won't moan if the list is extended during iteration...!
		while(src_iter.hasNext() ) {
			File src = src_iter.next();
			
			File[] allitems = src.listFiles();
			
			for(File f : allitems) {
				if( !allmode && f.getName().charAt(0) == '.' ) {continue;} // if we are not in 'all files' mode and the file is hidden, skip it
				
				// create the still hypothetical path of the destination file/directory
				File dest = new File(destination, relpath(f) );
				
				if(f.isDirectory()) {
					if(recursing) {// if we are recursing, create directory for further copying
						setlistadd(sources, f.getCanonicalFile() ); // add the directory to the sources list
						if(dest.mkdirs() ) { // make the destination directory
							if(verbose)System.out.println("MKDIR "+dest.getCanonicalPath());
						}
						// if the directory already exists, nothing will happen
					}
					continue; // don't try to write a directory file to a directory file
				}
				
				// check that a file is accepted by the patterns
				boolean auth = false;
				for(String pat : patterns) {
					if( auth = f.getName().matches(pat) )
						break; // we have found an accepting pattern, no need to check the rest
				}
				if(!auth) {
					if(verbose) {System.out.println("RJCTD: "+f.getName() );}
					continue;
				}
				
				// found a file worth copying
				found++;
				
				try {
					if(!dest.createNewFile() ) {
						switch(OWRITE) {
							case OW_ASK:
								System.out.println("Name conflict detected for "+dest.getCanonicalPath());
								System.out.print("Overwrite (y/n)? ");
								if( !conin.readLine().matches("y.*|Y.*") ) {continue;}
								break;
							case OW_YES:
								// keep on going
								break;
							case OW_NOT:
								continue; // don't overwrite data
							default:
								System.err.println("Unexpected option in overwrite - abort");
								System.exit(8);
						}
						System.out.println("Over-writing");
					}
					InputStream src_stream = new FileInputStream(f);
					OutputStream dest_stream = new FileOutputStream(dest);
					byte[] buf = new byte[4096];
					int bcount = -1;
					while( (bcount = src_stream.read(buf)) != -1 ) {
						dest_stream.write(buf,0,bcount);
						dest_stream.flush();
					}
					try {
						src_stream.close();
						dest_stream.close();
					} catch(IOException e) {}
				} catch (IOException e) {
					failed++;
					System.out.print("!### FAILED: ");
					System.out.print(f.getCanonicalPath() );
					System.out.println(" > "+dest.getCanonicalPath() );
					
					// delete the failed file
					if(!dest.delete()) {System.out.println("\tDeletion failed.");}
				}
			}
		}
		
		System.out.println("Found:\t"+found);
		System.out.println("Failed:\t"+failed);
		System.out.println("Success:\t"+ ((found-failed)*100/found)+"%" );
	}
	
	private static void addItem(String item) {
		try {
			File f = new File(item).getCanonicalFile();
			switch(MODE) {
				case MOD_S:
					if( !f.exists() ) {throw new FileNotFoundException("S:");}
					if( !f.isDirectory() ) {throw new IllegalArgumentException("S:");}
					
					setlistadd(sources,f);
					setlistadd(primary,f.getCanonicalPath() );// identify this source as a primary source
					if(verbose)System.out.println("Added source:\t"+f.getCanonicalPath());
					break;
				case MOD_D:
					//if( !f.exists() ) {throw new FileNotFoundException("D:");}
					if( !f.isDirectory() ) {throw new IllegalArgumentException("D:");}
					destination = f;
					if(verbose)System.out.println("Selected "+f.getPath()+" as destination folder.");
					break;
				case MOD_P:
					String pat = item.replaceAll("(\\(|\\)|\\[|\\]|\\.)","\\\\$1");// replace all regexp special meanings by escaped literals
					pat = pat.replaceAll("\\*",".*").replaceAll("\\?",".");// convert meanings of "any"
					setlistadd(patterns,pat);
					if(verbose)System.out.println("Added regex pattern: "+pat);
					break;
				default:
					System.err.println("Forbidden mode - program hacked :s");
					System.exit(9);
			}
		}
		catch(FileNotFoundException e) {System.err.println(e.getMessage()+"The file does not exist: "+item);}
		catch(IllegalArgumentException e) {System.err.println(e.getMessage()+"The path does not denote a directory: "+item);}
		catch(IOException e) {System.err.println("Could not get canonical path for "+item+"("+e.getMessage()+")");}
	}
	
	private static <T> void setlistadd(LinkedList<T> list, T item) {// only add an item if it is not already present
		if(list.contains(item) ) {
			if(verbose) System.out.println("Rejecting duplicate: "+item.toString() );
			}
		else {list.add(item);}
	}
	
	private static String relpath(File src) throws IOException {
		// src may be a secondary source. Identify and return the appropriate path start
		String path = src.getCanonicalPath();
		for(String base : primary) {
			if(path.indexOf(base) == 0) {
				return path.substring(base.length()+1 , path.length() );
			}
		}
		
		throw new IllegalArgumentException("Attempted to add a file whose parent is not a primary source: "+path);
	}
}

/** Inherently unsafe iterator.
 
 This is to counter the effect of the failsafe iterator with regards to a growing list */
class NFSIterator<E> implements Iterator {
	
	private LinkedList<E> list = null;
	private int idx = 0;
	
	public NFSIterator(LinkedList<E> l) {list = l;}
	
	public boolean hasNext() {return idx < list.size();}
	
	public E next() {return list.get(idx++);}
	
	public void remove() {} // does nothing
	
}