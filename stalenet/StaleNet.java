package stalenet;

import java.net.*;
import javax.net.ssl.*;
import java.io.*;

public class StaleNet extends Thread {
	
	private static boolean SEC = false;
	private static int port = 23;
	private static String host = "127.0.0.1";
	
	private BufferedReader netin = null;
	private PrintStream netout = null;
	
	public static void main(String[] args) {
		
		StringBuffer sb = new StringBuffer();
		for(int x=0;x<args.length;x++){sb.append(args[x]+" ");}
		
		java.util.regex.Matcher arlin =
			java.util.regex.Pattern.compile("([a-zA-Z0-9._-]+)(?:\\s+)?([0-9]+)?(?:\\s+)?(!)?").matcher(sb.toString());
		
		if(!arlin.find()) {help();return;}
		
		SEC = arlin.group(3) != null;
		port = arlin.group(2) != null?Integer.parseInt(arlin.group(2)):23;
		host = arlin.group(1);
		
		try {
			
			Socket s;
			if(SEC) {
				s = ( (SSLSocketFactory)SSLSocketFactory.getDefault() ).createSocket(host,port);
				((SSLSocket)s).startHandshake();
			} else {
				s = new Socket(host,port);
			}
			
			System.out.println("-- Established --");
			System.out.println();
			
			new StaleNet(s.getOutputStream() ).start();
			new StaleNet(s.getInputStream() ).start();
			
		} catch(Exception e) {
			System.err.println("!! Could not connect to "+host+" on port "+port+" !!");
		}
	}
	
	public static void help() {
		System.out.println("Use:\n\n%STALE_NET% host [port] [!]");
		System.out.println();
		System.out.println("%STALE_NET% - the command group used to start StaleNet. Can be"+
			"\n\tjava stalenet/Stalenet"+
			"\n\tjava -jar StaleNet.jar"+
			"\ndepending on the distribution format.");
		System.out.println();
		System.out.println("host - the host name or IP address to which to connect");
		System.out.println();
		System.out.println("port - the port to which to connect");
		System.out.println();
		System.out.println("'!' - Use secure socket connexion");
	}
	
	// threading
	
	public void run() {
		try {
			if(netout != null) {runout();}
			else if(netin != null) {runin();}
			else {System.exit(2);}// unexpected and unexplained error
		} catch (Exception e) {
			System.exit(1);// NetworkIO exception
		}
	}
	
	// For sending data
	protected StaleNet(OutputStream out) throws Exception {netout = new PrintStream(out);}
	
	protected void runout() throws Exception {
		BufferedReader conin = new BufferedReader( new InputStreamReader(System.in) );
		
		while(true) {netout.println( conin.readLine() );}
	}
	
	// For getting data
	protected StaleNet(InputStream in) throws Exception {netin = new BufferedReader(new InputStreamReader(in) );}
	
	protected void runin() throws Exception {
		while(true){
			String temp = netin.readLine();
			if(temp == null) {// end of stream -> connexion closed
				System.out.println("xX Connexion closed Xx");
				System.exit(0);
			}
			System.out.println( temp );
		}
	}
}
