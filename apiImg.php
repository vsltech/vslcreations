<?php
print_r($_FILES);
$img = $_FILES["file"]["tmp_name"];
$userid = $_GET["userid"];
echo $userid;
//echo "<br>";

if(move_uploaded_file($img,'user/'.$userid.'.jpg'))
{
	echo "400";
}
else
{
	echo "404";
}

?>
