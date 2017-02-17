import java.applet.*;
import java.io.File;
import java.awt.Desktop;
import javax.swing.JOptionPane;

public class EditOnline extends Applet{
  
   public static String getPath(String cmd) {
     String[] ms = {"C:\\Program Files\\Microsoft Office","C:\\Program Files (x86)\\Microsoft Office"}; 
     String[] of = {"Office","Office10","Office11","Office12","Office13","Office14","Office15","Office16"}; 
     for (int i=0; i< ms.length; i++) {
         File folderExisting = new File(ms[i]);
         if (folderExisting.exists()){ 
           for (int j=0; j< of.length; j++) {
             String tmp = ms[i]+"\\"+of[j]+"\\"+cmd;
             File fileExisting = new File(tmp);
             if (fileExisting.exists()){   
               return tmp;
             }
           }
         }       
     }
     String[] oo = {"C:\\Program Files\\OpenOffice.org 3\\program\\soffice.exe","C:\\Program Files (x86)\\OpenOffice.org 3\\program\\soffice.exe"}; 
     for (int i=0; i< oo.length; i++) {
       File folderExisting = new File(oo[i]);
       if (folderExisting.exists()){ 
         return oo[i];
       }
     }
     
     return cmd;
   }    
  
   public void init()  
   { 
     String filename = getParameter("filename"); 
     String[] ext = filename.split("\\.");
     if (ext.length>1){            
       try {
         String os = System.getProperty("os.name").toLowerCase();
         if (os.contains("win")) {
           String tmp = ext[ext.length-1].toLowerCase();
           String cmd = "soffice.exe";
           if ("doc".equals(tmp)||"docx".equals(tmp)||"rtf".equals(tmp)){
             cmd = "winword.exe";
           } else if ("xls".equals(tmp)||"xlsx".equals(tmp)){
             cmd = "excel.exe";
           } else if ("ppt".equals(tmp)||"pptx".equals(tmp)){
             cmd = "powerpnt.exe";
           } else {
             cmd = "soffice";
           }  
           
           try {
             String path = getPath(cmd);
             cmd = "\"" + path + "\"";
             Runtime.getRuntime().exec(cmd + " " + filename);
           } catch (Exception e){
             JOptionPane.showMessageDialog(null, e);
           }
           
         } else if (os.contains("nux") || os.contains("nix") || os.contains("mac")) {
           Runtime.getRuntime().exec("/usr/bin/open " + filename);
         } else {// Unknown OS, try with desktop
           if (Desktop.isDesktopSupported()){
             Desktop.getDesktop().open(new File(filename));
           } else {
             JOptionPane.showMessageDialog(null, "Khong ho tro tren he dieu hanh nay!");
           }
         }
       } catch (Exception e){
         JOptionPane.showMessageDialog(null, e);
       }
     }
   }  
   
   public static void main(String[] args){
   }
   
}